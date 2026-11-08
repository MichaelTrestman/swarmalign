"""Core metrics for SwarmAlign.

Pure functions, no file I/O and no network. Everything here operates on
cleaned choice data: one row per (agent, scenario) with the value that agent
chose. See group_metrics.py for the command-line entry point.

Definitions follow plan.md section 7.

Two readings of every quantity are computed:

  vector reading  goes through a Bradley-Terry fit of each agent's value
                  priorities, then measures Euclidean distance between the
                  fitted vectors.
  item reading    counts the share of scenarios two agents answered
                  differently. No model, no fit, no assumptions.

Reporting both is deliberate. If they agree, no conclusion rests on the
Bradley-Terry machinery. If they diverge, the fit is load-bearing and that
needs saying out loud.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

try:
    import choix
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    raise ImportError(
        "choix is required for the Bradley-Terry fit: pip install choix"
    ) from exc


REQUIRED_COLUMNS = ("agent_id", "scenario_id", "value1", "value2", "chose_value")

# alpha for choix.ilsr_pairwise. Matches ConflictScope's own call in
# src/analyze_experiment.py so our single-agent vectors reproduce theirs.
ILSR_ALPHA = 0.01


class FitError(RuntimeError):
    """A Bradley-Terry fit did not converge or had degenerate input."""


@dataclass(frozen=True)
class ChoiceData:
    """Cleaned choices for a group of agents over one shared scenario set.

    Attributes:
        values: the value names, in the fixed index order taken from the
            value-set JSON. Never inferred from observed data: a value that
            happens not to appear must still hold its index.
        agents: agent ids, in a stable order.
        scenario_ids: every scenario id present, sorted.
        pair_of: scenario_id -> (value1, value2) as written in the data.
        chosen: agent_id -> {scenario_id: chosen value name}.
    """

    values: tuple[str, ...]
    agents: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    pair_of: dict[str, tuple[str, str]]
    chosen: dict[str, dict[str, str]]
    value_index: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "value_index", {v: i for i, v in enumerate(self.values)}
        )

    @property
    def n_agents(self) -> int:
        return len(self.agents)

    def strata(self) -> dict[tuple[str, str], list[str]]:
        """Scenario ids grouped by unordered value pair.

        The bootstrap resamples within these groups so every value pair stays
        represented in every replicate.
        """
        out: dict[tuple[str, str], list[str]] = {}
        for sid in self.scenario_ids:
            a, b = self.pair_of[sid]
            out.setdefault(tuple(sorted((a, b))), []).append(sid)
        return out


def load_choices(
    frame: pd.DataFrame,
    values: Sequence[str],
    agents: Sequence[str] | None = None,
) -> ChoiceData:
    """Build a ChoiceData from a tidy cleaned-choices frame.

    Raises on anything clean.py should already have removed, rather than
    silently absorbing it: a row whose chosen value is not one of the two on
    offer is a bug upstream, not a data point.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"cleaned choices are missing columns: {missing}")

    unknown = set(frame["value1"]) | set(frame["value2"]) | set(frame["chose_value"])
    unknown -= set(values)
    if unknown:
        raise ValueError(f"values not in the value set: {sorted(unknown)}")

    bad = frame[
        (frame["chose_value"] != frame["value1"])
        & (frame["chose_value"] != frame["value2"])
    ]
    if len(bad):
        raise ValueError(
            f"{len(bad)} rows chose a value that was not one of the two offered; "
            "clean.py should have dropped these"
        )

    if agents is None:
        agents = sorted(frame["agent_id"].unique())
    else:
        absent = set(agents) - set(frame["agent_id"].unique())
        if absent:
            raise ValueError(f"no rows for requested agents: {sorted(absent)}")
        frame = frame[frame["agent_id"].isin(agents)]

    # Every agent must have answered the same scenarios: the whole design rests
    # on agents being compared on identical material.
    per_agent = {
        a: set(frame.loc[frame["agent_id"] == a, "scenario_id"]) for a in agents
    }
    shared = set.intersection(*per_agent.values()) if per_agent else set()
    for a, got in per_agent.items():
        if got != shared:
            raise ValueError(
                f"agent {a} answered {len(got)} scenarios but only {len(shared)} "
                "are shared across all agents; the comparison would not be paired"
            )
    if not shared:
        raise ValueError("no scenarios are shared across all requested agents")

    pair_of: dict[str, tuple[str, str]] = {}
    for sid, v1, v2 in frame[["scenario_id", "value1", "value2"]].itertuples(
        index=False
    ):
        prev = pair_of.setdefault(sid, (v1, v2))
        if prev != (v1, v2):
            raise ValueError(
                f"scenario {sid} carries two different value pairs: {prev} and {(v1, v2)}"
            )

    chosen = {
        a: dict(
            frame.loc[frame["agent_id"] == a, ["scenario_id", "chose_value"]].itertuples(
                index=False
            )
        )
        for a in agents
    }

    return ChoiceData(
        values=tuple(values),
        agents=tuple(agents),
        scenario_ids=tuple(sorted(shared)),
        pair_of=pair_of,
        chosen=chosen,
    )


def fit_theta(
    data: ChoiceData, agent: str, scenario_ids: Sequence[str] | None = None
) -> np.ndarray:
    """Bradley-Terry value vector for one agent, mean-centred.

    Each scenario is a match between the two values on offer; the chosen value
    wins. choix fits a latent strength per value from the pile of matches.

    The result is centred because Bradley-Terry strengths are only identified
    up to an additive constant: only differences between values mean anything,
    exactly as with Elo ratings.
    """
    sids = data.scenario_ids if scenario_ids is None else scenario_ids
    idx = data.value_index
    picks = data.chosen[agent]

    comparisons: list[tuple[int, int]] = []
    for sid in sids:
        v1, v2 = data.pair_of[sid]
        won = picks[sid]
        lost = v2 if won == v1 else v1
        comparisons.append((idx[won], idx[lost]))

    if not comparisons:
        raise FitError(f"no comparisons for agent {agent}")

    try:
        params = choix.ilsr_pairwise(
            len(data.values), comparisons, alpha=ILSR_ALPHA
        )
    except Exception as exc:  # choix raises a few different things
        raise FitError(f"Bradley-Terry fit failed for agent {agent}: {exc}") from exc

    theta = np.asarray(params, dtype=float)
    if not np.all(np.isfinite(theta)):
        raise FitError(f"Bradley-Terry fit produced non-finite values for {agent}")
    return theta - theta.mean()


def fit_all_thetas(
    data: ChoiceData, scenario_ids: Sequence[str] | None = None
) -> np.ndarray:
    """Stack of per-agent value vectors, shape (n_agents, n_values)."""
    return np.vstack([fit_theta(data, a, scenario_ids) for a in data.agents])


def goal_distance_matrix(thetas: np.ndarray) -> np.ndarray:
    """N x N Euclidean distances between value vectors.

    Symmetric, zero on the diagonal. This is the headline number, and it is
    meaningless without the noise floor: the formula never returns zero for two
    separately estimated vectors, even for the same agent measured twice.
    """
    diff = thetas[:, None, :] - thetas[None, :, :]
    return np.sqrt((diff**2).sum(axis=-1))


def item_disagreement_matrix(
    data: ChoiceData, scenario_ids: Sequence[str] | None = None
) -> np.ndarray:
    """N x N share of scenarios where two agents chose differently.

    The model-free reading. Needs no fit, so it survives rejecting
    Bradley-Terry entirely.
    """
    sids = data.scenario_ids if scenario_ids is None else scenario_ids
    n = data.n_agents
    picks = np.array(
        [[data.chosen[a][sid] for sid in sids] for a in data.agents], dtype=object
    )
    out = np.zeros((n, n))
    for i, j in combinations(range(n), 2):
        share = float(np.mean(picks[i] != picks[j]))
        out[i, j] = out[j, i] = share
    return out


def divergence_from_rest_vector(thetas: np.ndarray) -> np.ndarray:
    """R_i: distance from agent i to the mean of the other N-1 vectors."""
    n = thetas.shape[0]
    if n < 2:
        raise ValueError("divergence from the rest needs at least 2 agents")
    out = np.empty(n)
    for i in range(n):
        others = np.delete(thetas, i, axis=0)
        out[i] = float(np.linalg.norm(thetas[i] - others.mean(axis=0)))
    return out


def divergence_from_rest_item(
    data: ChoiceData, scenario_ids: Sequence[str] | None = None
) -> np.ndarray:
    """Q_i: per scenario, is agent i in the minority among the other N-1?

    Scores 1 where more of the others disagreed than agreed, 0.5 on a tie,
    0 otherwise, then averages over scenarios. For N = 2 this equals the
    pairwise item disagreement D_12.
    """
    sids = data.scenario_ids if scenario_ids is None else scenario_ids
    n = data.n_agents
    if n < 2:
        raise ValueError("divergence from the rest needs at least 2 agents")
    picks = [[data.chosen[a][sid] for sid in sids] for a in data.agents]
    out = np.zeros(n)
    for i in range(n):
        score = 0.0
        for k in range(len(sids)):
            mine = picks[i][k]
            same = sum(1 for j in range(n) if j != i and picks[j][k] == mine)
            diff = (n - 1) - same
            score += 1.0 if diff > same else (0.5 if diff == same else 0.0)
        out[i] = score / len(sids)
    return out


def dispersion(matrix: np.ndarray) -> float:
    """Mean of the upper triangle: how spread out the group is."""
    n = matrix.shape[0]
    if n < 2:
        raise ValueError("dispersion needs at least 2 agents")
    iu = np.triu_indices(n, k=1)
    return float(matrix[iu].mean())


def leave_one_out_drop(matrix: np.ndarray) -> np.ndarray:
    """L_i: group dispersion minus the dispersion of the other N-1 agents.

    Large positive values mark the agent holding the group apart. Needs N >= 3,
    since removing one of two agents leaves no pair.
    """
    n = matrix.shape[0]
    if n < 3:
        raise ValueError("leave-one-out drop needs at least 3 agents")
    whole = dispersion(matrix)
    out = np.empty(n)
    for i in range(n):
        keep = [j for j in range(n) if j != i]
        out[i] = whole - dispersion(matrix[np.ix_(keep, keep)])
    return out


# --------------------------------------------------------------------------
# Noise floor
# --------------------------------------------------------------------------


def split_half_distances(
    data: ChoiceData, agent: str, n_splits: int = 100, seed: int = 0
) -> np.ndarray:
    """Distance between an agent's vector and itself, over random half-splits.

    This is the noise floor. Any claimed difference between two agents has to
    clear it, otherwise the tool is reporting measurement error with a
    confident number attached. Splits are stratified by value pair so each half
    still covers every pair.
    """
    rng = np.random.default_rng(seed)
    strata = data.strata()
    out: list[float] = []
    for _ in range(n_splits):
        left: list[str] = []
        right: list[str] = []
        for sids in strata.values():
            shuffled = list(sids)
            rng.shuffle(shuffled)
            cut = len(shuffled) // 2
            left.extend(shuffled[:cut])
            right.extend(shuffled[cut:])
        if not left or not right:
            continue
        try:
            a = fit_theta(data, agent, left)
            b = fit_theta(data, agent, right)
        except FitError:
            continue
        out.append(float(np.linalg.norm(a - b)))
    return np.asarray(out)


# --------------------------------------------------------------------------
# Paired stratified bootstrap
# --------------------------------------------------------------------------


@dataclass
class BootstrapResult:
    """Replicate draws of every quantity, plus the count of skipped replicates."""

    thetas: np.ndarray  # (B, n_agents, n_values)
    goal_distance: np.ndarray  # (B, n_agents, n_agents)
    item_disagreement: np.ndarray
    divergence_vector: np.ndarray  # (B, n_agents)
    divergence_item: np.ndarray
    dispersion_vector: np.ndarray  # (B,)
    dispersion_item: np.ndarray
    loo_drop: np.ndarray | None  # (B, n_agents), None when N < 3
    skipped: int

    @property
    def n_replicates(self) -> int:
        return self.thetas.shape[0]


def _resample_ids(
    strata: dict[tuple[str, str], list[str]], rng: np.random.Generator
) -> list[str]:
    """One stratified resample of scenario ids, with replacement."""
    out: list[str] = []
    for sids in strata.values():
        out.extend(rng.choice(sids, size=len(sids), replace=True).tolist())
    return out


def bootstrap(
    data: ChoiceData, n_boot: int = 1000, seed: int = 0
) -> BootstrapResult:
    """Paired, stratified bootstrap over scenario ids.

    Each replicate draws one resampled scenario list and applies THE SAME list
    to every agent before refitting. That pairing is what makes the intervals
    intervals on a difference: agents stay compared on identical material, so
    the spread reflects scenario-sampling luck rather than agents being
    measured on different things.

    A replicate whose fit fails is skipped and counted, never silently
    replaced.
    """
    strata = data.strata()
    rng = np.random.default_rng(seed)
    n = data.n_agents

    thetas, gd, idis, dv, di, dispv, dispi, loo = [], [], [], [], [], [], [], []
    skipped = 0

    for _ in range(n_boot):
        sids = _resample_ids(strata, rng)
        try:
            th = fit_all_thetas(data, sids)
        except FitError:
            skipped += 1
            continue
        g = goal_distance_matrix(th)
        m = item_disagreement_matrix(data, sids)
        thetas.append(th)
        gd.append(g)
        idis.append(m)
        dv.append(divergence_from_rest_vector(th))
        di.append(divergence_from_rest_item(data, sids))
        dispv.append(dispersion(g))
        dispi.append(dispersion(m))
        if n >= 3:
            loo.append(leave_one_out_drop(g))

    if not thetas:
        raise FitError("every bootstrap replicate failed to fit")

    return BootstrapResult(
        thetas=np.asarray(thetas),
        goal_distance=np.asarray(gd),
        item_disagreement=np.asarray(idis),
        divergence_vector=np.asarray(dv),
        divergence_item=np.asarray(di),
        dispersion_vector=np.asarray(dispv),
        dispersion_item=np.asarray(dispi),
        loo_drop=np.asarray(loo) if loo else None,
        skipped=skipped,
    )


def interval(draws: np.ndarray, axis: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """2.5th and 97.5th percentiles of the bootstrap draws."""
    lo = np.percentile(draws, 2.5, axis=axis)
    hi = np.percentile(draws, 97.5, axis=axis)
    return lo, hi


# --------------------------------------------------------------------------
# Group summary over subsets
# --------------------------------------------------------------------------


def group_id(agents: Iterable[str]) -> str:
    """Stable name for a group: its sorted agent ids joined with '+'."""
    return "+".join(sorted(agents))
