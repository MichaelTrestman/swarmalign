"""Synthetic choice data with known value vectors.

Used by the tests and for exercising group_metrics.py end to end without
spending a single API call. Because the true vectors are known here, this is
also the only place where recovery can be checked directly: on real agents
there is nothing to compare the fitted vector against.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

DEFAULT_VALUES = (
    "autonomy",
    "authenticity",
    "creativity",
    "empowerment",
    "responsibility",
    "harmlessness",
    "compliance",
    "privacy",
)


def make_theta(
    n_values: int = 8, scale: float = 1.0, seed: int = 0
) -> np.ndarray:
    """A random mean-centred value vector."""
    rng = np.random.default_rng(seed)
    theta = rng.normal(0.0, scale, size=n_values)
    return theta - theta.mean()


def perturb(theta: np.ndarray, amount: float, seed: int = 0) -> np.ndarray:
    """Nudge a vector by a known amount, keeping it centred.

    `amount` is the Euclidean size of the nudge, so a caller can plant a
    difference of a stated magnitude and check the tool recovers the ordering.
    """
    rng = np.random.default_rng(seed)
    step = rng.normal(size=theta.shape)
    step -= step.mean()
    norm = np.linalg.norm(step)
    if norm == 0:  # pragma: no cover - vanishingly unlikely
        return theta.copy()
    return theta + step * (amount / norm)


def simulate_choices(
    thetas: dict[str, np.ndarray],
    n_scenarios: int = 400,
    values: tuple[str, ...] = DEFAULT_VALUES,
    seed: int = 0,
) -> pd.DataFrame:
    """Simulate forced-choice answers from known value vectors.

    Every agent answers the same scenarios, as the real design requires. For a
    scenario pitting value a against value b, an agent picks a with
    probability sigmoid(theta_a - theta_b), which is exactly the Bradley-Terry
    model the fit assumes. That makes this a recovery test of the estimator,
    not of the modelling assumption: if the real agents do not behave like
    this, these tests will not catch it.

    Scenarios are spread evenly over all value pairs, matching the stratified
    design.
    """
    rng = np.random.default_rng(seed)
    pairs = list(combinations(range(len(values)), 2))

    rows = []
    for k in range(n_scenarios):
        i, j = pairs[k % len(pairs)]
        sid = f"s{k:05d}_{values[i]}_{values[j]}"
        for agent, theta in thetas.items():
            p_i = 1.0 / (1.0 + np.exp(-(theta[i] - theta[j])))
            chose = values[i] if rng.random() < p_i else values[j]
            rows.append(
                {
                    "agent_id": agent,
                    "scenario_id": sid,
                    "value1": values[i],
                    "value2": values[j],
                    "chose_value": chose,
                }
            )
    return pd.DataFrame(rows)


def planted_outlier_group(
    n_same: int = 5,
    outlier_distance: float = 2.0,
    n_scenarios: int = 400,
    seed: int = 0,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """A group of near-identical agents plus one deliberately different agent.

    This mirrors gate G4: five paraphrase agents that should be
    indistinguishable, and one strongly steered agent the tool is supposed to
    find without being told which it is.
    """
    base = make_theta(seed=seed)
    thetas: dict[str, np.ndarray] = {}
    for k in range(n_same):
        # Tiny jitter so the "identical" agents are not bit-identical, which
        # would be an unrealistically easy case.
        thetas[f"p{k + 1}"] = perturb(base, amount=0.05, seed=seed + 100 + k)
    thetas["strong"] = perturb(base, amount=outlier_distance, seed=seed + 999)
    frame = simulate_choices(thetas, n_scenarios=n_scenarios, seed=seed + 1)
    return frame, thetas
