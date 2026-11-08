# SwarmAlign: What We Built and What It Showed

The group goal-distance tool from `plan.md` now exists, passes 15 offline tests, and runs end to end with no API calls. Running it surfaced two findings that change what the team should do before Sunday's spend: the assay looks underpowered at 400 scenarios, and gate G4 cannot pass as currently written.

## What this is

A program that takes the answers several AI agents gave to the same set of dilemmas and reports how far apart their priorities are — with error bars, and with a measurement of how much of the apparent difference is just noise.

That is the main deliverable named in `plan.md`. It now exists, it has 15 passing tests, and it runs end to end without touching the network or spending anything.

It was the right piece to build first because it has no external dependencies. No API keys, no spending decision, nobody else awake. Everything else in the plan waits on credentials or on a team call; this did not.

## How it works, in four steps

**1. Count the matches.** Every dilemma is a contest between two values — autonomy against responsibility, privacy against compliance. The agent picks one. That is a match result: *autonomy beat responsibility, for this agent, here.* Four hundred dilemmas give four hundred match results.

**2. Make a league table.** Feed those matches to the same mathematics chess uses for ratings. Out comes one rating per value — eight numbers saying how strongly that agent favours each. That is the agent's value profile. The technical name is Bradley-Terry, and it is Elo's statistical ancestor.

**3. Measure the gap.** Eight numbers is a point in space. Two agents are two points. The straight-line distance between them is the headline number.

**4. Check that the number means anything.** Split one agent's dilemmas in half, build a profile from each half, and measure the distance between that agent and itself. That is the noise floor: pure measurement error. Any real difference has to beat it.

The tool computes everything a second way as well, by counting how often two agents simply answered differently — no model at all. When both readings agree, no conclusion rests on believing Bradley-Terry. When they diverge, the fit is load-bearing and that needs saying.

## How to run it

Install the one dependency beyond the upstream pins:

```
pip install choix
```

Run the offline tests (no network, no API calls):

```
PYTHONPATH=. python3 -m pytest swarmalign/tests -q
```

Generate a synthetic six-agent group with a planted outlier and produce the tables:

```
PYTHONPATH=. python3 - <<'PY'
from swarmalign import synth
frame, _ = synth.planted_outlier_group(n_scenarios=400, seed=2)
import os; os.makedirs("swarmalign/results/demo_choices", exist_ok=True)
for a, g in frame.groupby("agent_id"):
    g.to_csv(f"swarmalign/results/demo_choices/{a}.csv", index=False)
PY

PYTHONPATH=. python3 -m swarmalign.group_metrics \
  --choices-dir swarmalign/results/demo_choices \
  --value-set value_sets/personalprotective.json \
  --boot 300 --seed 0 --splits 40 \
  --out swarmalign/results/demo
```

On real data, point `--choices-dir` at the cleaned per-agent choice CSVs instead. Expected columns: `agent_id`, `scenario_id`, `value1`, `value2`, `chose_value`. The tool refuses input where agents answered different scenarios, since the comparison would not be paired.

## What the test run showed

The test group was six synthetic agents: five near-copies of each other plus one deliberately different agent hidden among them. That is exactly the shape gate G4 is built to catch.

**The machinery works.** The planted outlier came out ranked first on every measure, on both the model-based reading and the plain-counting reading.

### Finding 1: 400 scenarios is probably not enough

Two identical agents measure roughly 0.7 to 1.2 apart from noise alone. In the six-agent run, **8 of the 15 pairs sat closer together than an agent sits to itself**. Those pairs are indistinguishable; the tool is reporting measurement error with a confident number attached.

The lever is scenario count:

| Scenarios per agent | Distance between two identical agents |
| --- | --- |
| 100 | 1.44 |
| 200 | 1.18 |
| 400 | 0.71 |
| 800 | 0.48 |
| 1600 | 0.45 |

The honest caveat, which we should state before anyone else does: the synthetic agents use an arbitrary scale, so this does not say whether *real* models differ by more or less than 0.7. Nobody knows until someone runs it.

That is precisely why it belongs in the smoke test. The first question is not "does the pipeline run" but "do real agents differ by more than measurement error". If they do not, the full 14,400-call run buys nothing — and that is worth learning for 120 calls rather than 14,400.

### Finding 2: G4 cannot pass as written

G4 requires the planted outlier's lower interval bound to sit above every paraphrase agent's upper bound, on both readings. With an outlier planted at distance 2.0 — about as obvious as one could plant:

| Reading | Outlier lower bound | Highest paraphrase upper bound | Passes? |
| --- | --- | --- | --- |
| Vector | 1.635 | 2.129 | No |
| Item | 0.263 | 0.312 | No |

It fails, and not because the tool missed anything. The outlier ranked first on every point estimate. At 400 scenarios the intervals are simply too wide to clear each other, so the gate is testing the sample size rather than the instrument.

G4 will therefore fail on Sunday however well the tool performs. Either the threshold moves to something the data can support — outlier ranks first on both readings, intervals allowed to overlap — or the scenario count rises substantially. **This has to be decided before the run**, because `plan.md` rightly forbids moving a threshold after seeing the result.

### Finding 3: a cosmetic problem that reads as a bug

Group dispersion came out at 1.398 with an interval of [1.426, 2.065] — the estimate sits below its own lower bound.

This is not a coding error. Distance between two separately estimated vectors is biased upward, because estimation error in each vector adds to the real separation and can only push the norm up. The bootstrap resamples scenarios, so it captures spread around the *estimate*, not the gap between estimate and truth. Resampling with replacement inflates it further.

The consequence is presentational but real: a judge glancing at that table will think the code is broken. It needs either a bias correction or a sentence of explanation in the write-up.

## Three things for the team

None of these is a caveat. Each is a decision with a deadline.

1. **The plan's main artifact exists and is tested.** Sunday can start from running code rather than a blank file.
2. **Measure the noise floor in the smoke test, before committing the budget.** It is the cheapest available check on whether the full run is worth paying for, and it costs about 120 calls.
3. **Set G4's threshold tonight, not Sunday.** It cannot pass as written, and moving it after the run would invalidate it.

The contribution here is not an opinion about the design. It is a statement about what the numbers can and cannot support, demonstrated by running the thing.

## The files

Everything sits in a new top-level `swarmalign/` folder. ConflictScope's `src/`, `data/`, `scripts/` and `value_sets/` are untouched, so the prior-work boundary the hackathon rules require stays clean.

| Path | What it is |
| --- | --- |
| `swarmalign/metrics.py` | The mathematics: Bradley-Terry fit, distances, divergence, dispersion, bootstrap, noise floor |
| `swarmalign/group_metrics.py` | Command-line tool; writes the tables fixed in plan.md section 7 |
| `swarmalign/synth.py` | Synthetic agents with known value vectors, for testing without API calls |
| `swarmalign/tests/test_metrics.py` | 15 offline tests |
| `swarmalign/results/demo/` | Output tables from the run described above |

One note on the tests. The synthetic agents are generated from exactly the Bradley-Terry model the fit assumes, so passing means the arithmetic recovers what was planted. It does not mean real agents behave that way. That distinction belongs in the write-up.
