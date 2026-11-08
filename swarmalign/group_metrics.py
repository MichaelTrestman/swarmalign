"""Group goal-distance tables for a set of agents.

Reads cleaned choices, writes the tables defined in plan.md section 7. Makes
no model calls: everything here runs offline from saved answers, so it can be
re-run freely while the assay is still being collected.

Usage:

    python -m swarmalign.group_metrics \\
        --choices-dir swarmalign/results/choices \\
        --agents a1 a2 a3 a4 a5 a6 \\
        --boot 1000 --seed 0 \\
        --out swarmalign/results/main/

The column names of group.csv and agent_vs_rest.csv are a published
interface: the later swarm experiment reads them. Do not rename them without
updating SCHEMA.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics
from .metrics import ChoiceData, FitError

DEFAULT_VALUE_SET = Path("value_sets/personalprotective.json")


# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------


def load_value_names(path: Path) -> tuple[str, ...]:
    """Fixed value index, taken from the value-set file.

    Deliberately not inferred from the observed data: a value that no agent
    ever picked must still occupy its slot, or two runs would produce vectors
    in different bases and their distance would be meaningless.
    """
    with path.open() as fh:
        return tuple(json.load(fh).keys())


def read_choices_dir(path: Path) -> pd.DataFrame:
    """Concatenate every CSV of cleaned choices under a directory."""
    files = sorted(path.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no CSV files in {path}")
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------


def agent_vectors_table(
    data: ChoiceData, thetas: np.ndarray, boot: metrics.BootstrapResult
) -> pd.DataFrame:
    lo, hi = metrics.interval(boot.thetas)
    n_comparisons = len(data.scenario_ids)
    rows = []
    for i, agent in enumerate(data.agents):
        for v, value in enumerate(data.values):
            rows.append(
                {
                    "agent_id": agent,
                    "value": value,
                    "score": thetas[i, v],
                    "score_lo": lo[i, v],
                    "score_hi": hi[i, v],
                    "n_comparisons": n_comparisons,
                }
            )
    return pd.DataFrame(rows)


def pairwise_table(
    data: ChoiceData,
    gd: np.ndarray,
    idis: np.ndarray,
    boot: metrics.BootstrapResult,
) -> pd.DataFrame:
    gd_lo, gd_hi = metrics.interval(boot.goal_distance)
    id_lo, id_hi = metrics.interval(boot.item_disagreement)
    rows = []
    for i, j in combinations(range(data.n_agents), 2):
        rows.append(
            {
                "agent_i": data.agents[i],
                "agent_j": data.agents[j],
                "goal_distance": gd[i, j],
                "goal_distance_lo": gd_lo[i, j],
                "goal_distance_hi": gd_hi[i, j],
                "item_disagreement": idis[i, j],
                "item_disagreement_lo": id_lo[i, j],
                "item_disagreement_hi": id_hi[i, j],
            }
        )
    return pd.DataFrame(rows)


def agent_vs_rest_table(
    data: ChoiceData,
    gd: np.ndarray,
    boot: metrics.BootstrapResult,
    thetas: np.ndarray,
) -> pd.DataFrame:
    gid = metrics.group_id(data.agents)
    dv = metrics.divergence_from_rest_vector(thetas)
    di = metrics.divergence_from_rest_item(data)
    dv_lo, dv_hi = metrics.interval(boot.divergence_vector)
    di_lo, di_hi = metrics.interval(boot.divergence_item)

    if data.n_agents >= 3:
        loo = metrics.leave_one_out_drop(gd)
        loo_lo, loo_hi = metrics.interval(boot.loo_drop)
    else:
        loo = loo_lo = loo_hi = np.full(data.n_agents, np.nan)

    rows = []
    for i, agent in enumerate(data.agents):
        rows.append(
            {
                "agent_id": agent,
                "group_id": gid,
                "divergence_vector": dv[i],
                "divergence_vector_lo": dv_lo[i],
                "divergence_vector_hi": dv_hi[i],
                "divergence_item": di[i],
                "divergence_item_lo": di_lo[i],
                "divergence_item_hi": di_hi[i],
                "loo_drop_vector": loo[i],
                "loo_drop_lo": loo_lo[i],
                "loo_drop_hi": loo_hi[i],
            }
        )
    return pd.DataFrame(rows)


def group_row(
    agents: tuple[str, ...],
    disp_v: float,
    disp_i: float,
    boot_disp_v: np.ndarray,
    boot_disp_i: np.ndarray,
) -> dict:
    v_lo, v_hi = metrics.interval(boot_disp_v)
    i_lo, i_hi = metrics.interval(boot_disp_i)
    return {
        "group_id": metrics.group_id(agents),
        "n_agents": len(agents),
        "dispersion_vector": disp_v,
        "dispersion_vector_lo": float(v_lo),
        "dispersion_vector_hi": float(v_hi),
        "dispersion_item": disp_i,
        "dispersion_item_lo": float(i_lo),
        "dispersion_item_hi": float(i_hi),
    }


def subset_group_rows(
    data: ChoiceData, boot: metrics.BootstrapResult, size: int
) -> list[dict]:
    """One group row per subset of the given size.

    Reuses the bootstrap draws already computed for the whole group rather
    than refitting, which is why the replicate thetas are kept: the later
    experiment wants a predictor for each candidate swarm, and refitting every
    subset separately would cost far more for the same numbers.
    """
    rows = []
    for combo in combinations(range(data.n_agents), size):
        names = tuple(data.agents[i] for i in combo)
        sel = np.ix_(combo, combo)
        gd_sub = metrics.goal_distance_matrix(
            metrics.fit_all_thetas(
                ChoiceData(
                    values=data.values,
                    agents=names,
                    scenario_ids=data.scenario_ids,
                    pair_of=data.pair_of,
                    chosen={a: data.chosen[a] for a in names},
                )
            )
        )
        idis_sub = metrics.item_disagreement_matrix(
            ChoiceData(
                values=data.values,
                agents=names,
                scenario_ids=data.scenario_ids,
                pair_of=data.pair_of,
                chosen={a: data.chosen[a] for a in names},
            )
        )
        bv = np.array(
            [metrics.dispersion(g[sel]) for g in boot.goal_distance]
        )
        bi = np.array(
            [metrics.dispersion(m[sel]) for m in boot.item_disagreement]
        )
        rows.append(
            group_row(
                names,
                metrics.dispersion(gd_sub),
                metrics.dispersion(idis_sub),
                bv,
                bi,
            )
        )
    return rows


def noise_floor_table(
    data: ChoiceData, n_splits: int, seed: int
) -> pd.DataFrame:
    """Per-agent distance from an agent to itself, over random half-splits.

    Distances between separately estimated vectors are biased upward, so a
    pairwise distance only means something measured against this.
    """
    rows = []
    for agent in data.agents:
        d = metrics.split_half_distances(
            data, agent, n_splits=n_splits, seed=seed
        )
        rows.append(
            {
                "agent_id": agent,
                "split_half_distance_median": float(np.median(d)) if len(d) else np.nan,
                "split_half_distance_p95": float(np.percentile(d, 95))
                if len(d)
                else np.nan,
                "n_splits_used": int(len(d)),
            }
        )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Group goal-distance tables from cleaned ConflictScope choices."
    )
    p.add_argument(
        "--choices-dir",
        type=Path,
        required=True,
        help="directory of cleaned per-agent choice CSVs",
    )
    p.add_argument(
        "--agents",
        nargs="+",
        default=None,
        help="agent ids to include; default is every agent found",
    )
    p.add_argument(
        "--value-set",
        type=Path,
        default=DEFAULT_VALUE_SET,
        help="ConflictScope value-set JSON, for the fixed value index",
    )
    p.add_argument("--boot", type=int, default=1000, help="bootstrap replicates")
    p.add_argument("--seed", type=int, default=0, help="seed for every random step")
    p.add_argument(
        "--splits",
        type=int,
        default=100,
        help="random half-splits per agent for the noise floor",
    )
    p.add_argument(
        "--subsets-of-size",
        type=int,
        default=None,
        help="also write one group row per subset of this size",
    )
    p.add_argument("--out", type=Path, required=True, help="output directory")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    values = load_value_names(args.value_set)
    frame = read_choices_dir(args.choices_dir)
    data = metrics.load_choices(frame, values, args.agents)

    print(
        f"{data.n_agents} agents, {len(data.scenario_ids)} shared scenarios, "
        f"{len(data.values)} values",
        file=sys.stderr,
    )

    thetas = metrics.fit_all_thetas(data)
    gd = metrics.goal_distance_matrix(thetas)
    idis = metrics.item_disagreement_matrix(data)

    print(f"bootstrapping {args.boot} replicates...", file=sys.stderr)
    boot = metrics.bootstrap(data, n_boot=args.boot, seed=args.seed)
    if boot.skipped:
        print(
            f"warning: {boot.skipped} replicates skipped on fit failure",
            file=sys.stderr,
        )

    agent_vectors_table(data, thetas, boot).to_csv(
        args.out / "agent_vectors.csv", index=False
    )
    pairwise_table(data, gd, idis, boot).to_csv(
        args.out / "pairwise.csv", index=False
    )
    agent_vs_rest_table(data, gd, boot, thetas).to_csv(
        args.out / "agent_vs_rest.csv", index=False
    )

    rows = [
        group_row(
            data.agents,
            metrics.dispersion(gd),
            metrics.dispersion(idis),
            boot.dispersion_vector,
            boot.dispersion_item,
        )
    ]
    if args.subsets_of_size:
        rows.extend(subset_group_rows(data, boot, args.subsets_of_size))
    pd.DataFrame(rows).to_csv(args.out / "group.csv", index=False)

    print(f"noise floor: {args.splits} half-splits per agent...", file=sys.stderr)
    floor = noise_floor_table(data, args.splits, args.seed)
    floor.to_csv(args.out / "noise_floor.csv", index=False)
    _warn_on_power(gd, floor, data)

    np.savez_compressed(
        args.out / "boot_draws.npz",
        thetas=boot.thetas,
        goal_distance=boot.goal_distance,
        item_disagreement=boot.item_disagreement,
        divergence_vector=boot.divergence_vector,
        divergence_item=boot.divergence_item,
        dispersion_vector=boot.dispersion_vector,
        dispersion_item=boot.dispersion_item,
        agents=np.array(data.agents),
        values=np.array(data.values),
    )

    meta = {
        "agents": list(data.agents),
        "values": list(data.values),
        "n_scenarios": len(data.scenario_ids),
        "scenario_subset_sha256": _digest(data.scenario_ids),
        "n_boot_requested": args.boot,
        "n_boot_used": boot.n_replicates,
        "skipped_replicates": boot.skipped,
        "seed": args.seed,
        "n_splits": args.splits,
        "value_set": str(args.value_set),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2))

    print(f"wrote tables to {args.out}", file=sys.stderr)
    return 0


def _warn_on_power(
    gd: np.ndarray, floor: pd.DataFrame, data: ChoiceData
) -> None:
    """Say plainly when the measured differences do not clear measurement error.

    Distances between separately estimated vectors are inflated by estimation
    noise, so a pairwise distance at or below an agent's own split-half
    distance is consistent with the two agents being identical. G3 formalises
    this; printing it here means nobody has to wait for validate.py to find
    out the assay was underpowered.
    """
    med = float(np.median(floor["split_half_distance_median"].dropna()))
    iu = np.triu_indices(data.n_agents, k=1)
    pairs = gd[iu]
    if not len(pairs):
        return
    print(
        "note: distances between separately estimated vectors are biased "
        "upward, so a point estimate can fall below its own bootstrap "
        "interval. Compare distances with each other and with the floor, "
        "never read one as an unbiased separation.",
        file=sys.stderr,
    )
    under = int((pairs <= med).sum())
    print(
        f"noise floor (median split-half distance): {med:.3f}; "
        f"pairwise distances span {pairs.min():.3f} to {pairs.max():.3f}",
        file=sys.stderr,
    )
    if under:
        print(
            f"WARNING: {under} of {len(pairs)} agent pairs are no further apart "
            "than an agent is from itself. Those pairs are indistinguishable at "
            "this scenario count; raising the scenario count is the lever.",
            file=sys.stderr,
        )


def _digest(ids: tuple[str, ...]) -> str:
    import hashlib

    h = hashlib.sha256()
    for sid in sorted(ids):
        h.update(sid.encode())
    return h.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
