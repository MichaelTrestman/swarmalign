"""Offline tests for the group metrics. No API calls, no network.

These check the estimator, not the modelling assumption. The synthetic agents
are generated from exactly the Bradley-Terry model the fit assumes, so passing
means the arithmetic recovers what was planted. It does not mean real agents
behave this way.
"""

from __future__ import annotations

import numpy as np
import pytest

from swarmalign import metrics, synth
from swarmalign.synth import DEFAULT_VALUES


def build(thetas, n_scenarios=400, seed=0):
    frame = synth.simulate_choices(thetas, n_scenarios=n_scenarios, seed=seed)
    return metrics.load_choices(frame, DEFAULT_VALUES)


# --------------------------------------------------------------------------
# Recovery
# --------------------------------------------------------------------------


def test_goal_distance_is_biased_upward():
    """Estimated distances overstate true distances, systematically.

    This is a characterization test, not an aspiration. Distance between two
    separately estimated noisy vectors is inflated: estimation error in each
    vector adds in quadrature to the real separation and can only push the
    norm up, never down. Measured here at 400 scenarios, the inflation runs
    around +0.3 on a true distance of 1.5, roughly 20 percent.

    The consequence matters more than the number. The bootstrap resamples
    scenarios, so it captures sampling spread around the ESTIMATE, not the
    gap between the estimate and the truth. A 95 percent interval therefore
    under-covers the true distance, and every miss is on the high side.

    Nothing downstream should read a raw distance as an unbiased measure of
    how far apart two agents really are. Distances are for COMPARING pairs
    against each other and against the noise floor, which carries the same
    inflation and so cancels much of it.
    """
    trials = 12
    bias = []
    covered = 0
    for t in range(trials):
        a = synth.make_theta(seed=t)
        b = synth.perturb(a, amount=1.5, seed=100 + t)
        data = build({"a": a, "b": b}, n_scenarios=400, seed=200 + t)
        thetas = metrics.fit_all_thetas(data)
        est = metrics.goal_distance_matrix(thetas)[0, 1]
        true_d = float(np.linalg.norm(a - b))
        bias.append(est - true_d)

        boot = metrics.bootstrap(data, n_boot=120, seed=t)
        lo, hi = metrics.interval(boot.goal_distance)
        covered += lo[0, 1] <= true_d <= hi[0, 1]

    assert np.mean(bias) > 0.15, (
        f"expected a clear upward bias, got {np.mean(bias):+.3f}"
    )
    assert sum(b > 0 for b in bias) >= trials - 2, (
        "bias should be upward in nearly every trial"
    )
    # Documented, not desired: a nominal 95% interval does not reach 95% here.
    assert covered < trials, (
        "coverage was perfect, so the known upward bias has gone away; "
        "re-derive the bias note in the write-up before relaxing this test"
    )


def test_noise_floor_shrinks_with_more_scenarios():
    """The floor is a function of how much data each fit sees.

    Measured medians for two identical agents: about 1.4 at 100 scenarios,
    0.7 at 400, 0.45 at 1600. This is the number that decides whether the
    assay has the power to separate real agents at all, so it is worth
    measuring early and cheaply rather than after the full spend.
    """
    theta = synth.make_theta(seed=0)
    floors = []
    for n in (100, 400, 1600):
        data = build({"a": theta, "b": theta}, n_scenarios=n, seed=5)
        observed = metrics.goal_distance_matrix(metrics.fit_all_thetas(data))[0, 1]
        floors.append(observed)
    assert floors[0] > floors[1] > floors[2], (
        f"floor did not fall with more scenarios: {floors}"
    )


def test_identical_agents_sit_near_the_noise_floor():
    """Two agents with the same true vector are not pushed apart by the fit."""
    theta = synth.make_theta(seed=3)
    data = build({"a": theta, "b": theta}, n_scenarios=400, seed=11)
    thetas = metrics.fit_all_thetas(data)
    observed = metrics.goal_distance_matrix(thetas)[0, 1]
    floor = np.median(metrics.split_half_distances(data, "a", n_splits=40, seed=1))
    assert observed <= floor * 1.5, (
        f"distance between identical agents ({observed:.3f}) far exceeds the "
        f"noise floor ({floor:.3f})"
    )


def test_distance_grows_with_planted_difference():
    """Mild, medium and strong perturbations come back in that order."""
    base = synth.make_theta(seed=5)
    agents = {"base": base}
    for name, amount in (("mild", 0.4), ("medium", 1.2), ("strong", 2.4)):
        agents[name] = synth.perturb(base, amount=amount, seed=hash(name) % 1000)
    data = build(agents, n_scenarios=600, seed=7)
    thetas = metrics.fit_all_thetas(data)
    gd = metrics.goal_distance_matrix(thetas)
    i = {a: k for k, a in enumerate(data.agents)}
    d_mild = gd[i["base"], i["mild"]]
    d_medium = gd[i["base"], i["medium"]]
    d_strong = gd[i["base"], i["strong"]]
    assert d_mild < d_medium < d_strong


# --------------------------------------------------------------------------
# G4 logic
# --------------------------------------------------------------------------


def test_planted_outlier_is_found():
    """The steered agent has the highest divergence on both readings."""
    frame, _ = synth.planted_outlier_group(n_scenarios=400, seed=2)
    data = metrics.load_choices(frame, DEFAULT_VALUES)
    thetas = metrics.fit_all_thetas(data)
    dv = metrics.divergence_from_rest_vector(thetas)
    di = metrics.divergence_from_rest_item(data)
    strong = data.agents.index("strong")
    assert int(np.argmax(dv)) == strong, "vector reading missed the outlier"
    assert int(np.argmax(di)) == strong, "item reading missed the outlier"


def test_no_outlier_when_all_agents_match():
    """G4's logic must fail when there is nothing planted to find.

    A test that only ever passes proves nothing, so this checks the negative
    case: with no real outlier, the 'strong' agent is not reliably extreme.
    """
    base = synth.make_theta(seed=8)
    agents = {f"p{k}": synth.perturb(base, 0.05, seed=300 + k) for k in range(5)}
    agents["strong"] = synth.perturb(base, 0.05, seed=999)
    data = build(agents, n_scenarios=400, seed=13)
    thetas = metrics.fit_all_thetas(data)
    dv = metrics.divergence_from_rest_vector(thetas)
    spread = dv.max() - dv.min()
    assert spread < 0.6, (
        "agents with no planted difference still spread widely; the gate would "
        "pass on noise"
    )


# --------------------------------------------------------------------------
# Structure and edge cases
# --------------------------------------------------------------------------


def test_distance_matrix_is_a_metric_shape():
    data = build({"a": synth.make_theta(seed=1), "b": synth.make_theta(seed=2)})
    gd = metrics.goal_distance_matrix(metrics.fit_all_thetas(data))
    assert gd[0, 0] == pytest.approx(0.0)
    assert gd[1, 1] == pytest.approx(0.0)
    assert gd[0, 1] == pytest.approx(gd[1, 0])


def test_q_equals_d_for_two_agents():
    """For N = 2 the item divergence reduces to the pairwise disagreement."""
    data = build({"a": synth.make_theta(seed=1), "b": synth.make_theta(seed=2)})
    q = metrics.divergence_from_rest_item(data)
    d = metrics.item_disagreement_matrix(data)[0, 1]
    assert q[0] == pytest.approx(d)
    assert q[1] == pytest.approx(d)


def test_theta_is_centred():
    data = build({"a": synth.make_theta(seed=4)})
    theta = metrics.fit_theta(data, "a")
    assert theta.mean() == pytest.approx(0.0, abs=1e-9)


def test_same_seed_gives_identical_output():
    data = build({"a": synth.make_theta(seed=1), "b": synth.make_theta(seed=2)})
    first = metrics.bootstrap(data, n_boot=50, seed=42)
    second = metrics.bootstrap(data, n_boot=50, seed=42)
    assert np.allclose(first.goal_distance, second.goal_distance)


def test_loo_drop_needs_three_agents():
    data = build({"a": synth.make_theta(seed=1), "b": synth.make_theta(seed=2)})
    gd = metrics.goal_distance_matrix(metrics.fit_all_thetas(data))
    with pytest.raises(ValueError):
        metrics.leave_one_out_drop(gd)


def test_value_index_comes_from_the_value_set_not_the_data():
    """A value nobody ever picked still holds its slot in the vector."""
    base = synth.make_theta(seed=6)
    frame = synth.simulate_choices({"a": base}, n_scenarios=400, seed=6)
    # Drop every scenario touching 'privacy' so that value never appears.
    frame = frame[(frame["value1"] != "privacy") & (frame["value2"] != "privacy")]
    data = metrics.load_choices(frame, DEFAULT_VALUES)
    assert len(data.values) == 8
    assert data.value_index["privacy"] == 7
    theta = metrics.fit_theta(data, "a")
    assert theta.shape == (8,)


def test_rejects_rows_choosing_an_offered_value_that_was_not_offered():
    frame = synth.simulate_choices({"a": synth.make_theta(seed=1)}, n_scenarios=60)
    frame.loc[0, "chose_value"] = "privacy" if frame.loc[0, "value1"] != "privacy" else "autonomy"
    if frame.loc[0, "chose_value"] not in (frame.loc[0, "value1"], frame.loc[0, "value2"]):
        with pytest.raises(ValueError, match="not one of the two offered"):
            metrics.load_choices(frame, DEFAULT_VALUES)


def test_rejects_unpaired_agents():
    """Agents answering different scenarios would break the paired design."""
    frame = synth.simulate_choices(
        {"a": synth.make_theta(seed=1), "b": synth.make_theta(seed=2)},
        n_scenarios=100,
    )
    frame = frame.drop(frame[(frame["agent_id"] == "b")].index[:5])
    with pytest.raises(ValueError, match="would not be paired"):
        metrics.load_choices(frame, DEFAULT_VALUES)


def test_bootstrap_is_paired_across_agents():
    """Every agent is refit on the same resampled scenario list each replicate.

    Checked indirectly: two agents with identical true vectors should have a
    bootstrap distance distribution concentrated near the noise floor. An
    unpaired bootstrap would inflate it.
    """
    theta = synth.make_theta(seed=9)
    data = build({"a": theta, "b": theta}, n_scenarios=400, seed=21)
    boot = metrics.bootstrap(data, n_boot=100, seed=0)
    floor = np.median(metrics.split_half_distances(data, "a", n_splits=40, seed=1))
    assert np.median(boot.goal_distance[:, 0, 1]) <= floor * 1.5
