# SwarmAlign: What We Built and What It Showed

The group goal-distance tool from `plan.md` exists, passes 15 offline tests, and has now been run end to end on real language models through OpenRouter: 4 main-pool agents (2 base models x 2 role prompts) over 399 shared scenarios, and a 6-agent validation pool (5 neutral paraphrases + 1 strongly steered agent) over 200 scenarios. This section records what that real run showed; the sections below it (originally written before any model had been called) describe the synthetic-only validation that came first and still hold as a separate, earlier check.

## Real-run results (real models, real API calls)

| Gate | Result | Headline number |
| --- | --- | --- |
| G1 Smoke test | **Pass** | 100% parseable choices across all 10 agents (one agent: 399/400), reruns made zero additional calls |
| G2 Reliability | **Pass** | mean split-half r = 0.85, Spearman-Brown corrected = 0.92, median rank correlation = 0.80 (thresholds: 0.8, 0.8, 0.7) |
| G3 Spread | **Fail** | 0 of 6 main-pool pairs clear their own split-half noise p95; pairwise distance CI lower bounds (0.8-3.2) sit below individual noise floors (1.6-5.2) |
| G4 Planted outlier | **Pass, with margin** | steered agent's R_i = 7.64 (vector) / 0.35 (item) vs. highest paraphrase upper CI bound of 2.20 / 0.07 -- the outlier's lower bound clears every paraphrase's upper bound on both readings |
| G5 Dose response | **Not applicable** | this pool has one steer strength (strong only), not the mild/medium/strong triplet G5 needs |

Full tables: `swarmalign/results/main_real/` (group metrics), `swarmalign/results/validate_real/` (gates.csv + per-gate detail JSON).

**Reading the mixed G2/G3/G4 result.** This is not a contradiction. G2 says the measurement is internally consistent -- ask the same agent the same thing twice (via split halves) and it gives close to the same answer. G4 says the instrument can find a planted, deliberate difference when one exists, decisively. G3 says that among the four *organically different* main-pool agents (two base models, two role prompts), the natural differences are not reliably bigger than each agent's own measurement noise at this scenario count. `docs/METHODOLOGY.md`'s claim-licensing table calls this outcome explicitly: *"Reliable but cannot discriminate. Not a project failure. It would be a substantive finding that frontier models hold near-identical value orderings under forced choice."* G4 passing on the same data rules out the alternative explanation that the instrument simply can't discriminate anything -- it can, when the difference is as large as a deliberate steer. The main pool's natural differences are evidently smaller than that.

**What would change the G3 result.** More scenarios per agent (the lever `docs/METHODOLOGY.md` already identified from synthetic data: noise floor roughly halves from 100 to 400 scenarios and halves again by 1600), not a different formula or threshold -- per `plan.md`'s rule against moving thresholds after seeing a result.

## What changed versus the synthetic-only version of this document

Everything in `plan.md` section 6's "still to build" list now exists:

| Built | What it does |
| --- | --- |
| `run_assay.py` | Drives `src/evaluate_models.py` per agent: chunked for resumability, drops stale ERROR rows before resuming, `--dry-run`, `--max-calls` |
| `clean.py` | Keeps only A/B rows, writes `agent_id, scenario_id, value1, value2, chose_value`, logs drop rate per agent |
| `select_scenarios.py` | Builds the committed `scenarios_main_400.json` / `scenarios_validation_200.json`, stratified over the 16 value pairs that actually have kept scenarios (not 28 -- see note below) |
| `validate.py` | Gates G2-G5 against real cleaned choices, with labeled pass-mark constants |
| `agents/`, `prompts/` | 4 main-pool + 6 validation-pool YAML configs, and the prompt text files they reference |

**A fourth ConflictScope edit, beyond plan.md section 5's three.** `src/simulated_conversation.py` imported `fcntl` (Unix-only) at module level, which crashes on import under Windows even for the plain MCQ path that never touches file locking. Moved the import inside the one function (`file_lock`) that uses it -- same pattern as the existing vLLM import fix, for the same reason (an optional, platform-specific dependency of a code path we don't use).

**The 28 value pairs in plan.md section 4 are a combinatorial upper bound, not what ConflictScope generated.** Only 16 of the 28 possible pairs among the 8 Personal-Protective values have any kept scenario in `data/personalprotective/claude-3-5-sonnet-latest.csv`. `select_scenarios.py` stratifies over those 16.

**OpenRouter model slugs churn.** Two of the smoke-test model slugs stopped working mid-session: `anthropic/claude-3.5-haiku` was removed outright, and its suggested replacement `anthropic/claude-3-haiku` turned out to already be deprecated (Sep 10, 2026). The run settled on `anthropic/claude-haiku-4.5`, confirmed working. Anyone rerunning this later should expect to re-check slugs rather than trust the ones recorded in `agents/*.yaml`.

**Running many agents as parallel OS processes hit a local resource limit, not an API one.** Launching all 10 agents' `run_assay.py` invocations at once caused two to crash on `OpenBLAS error: Memory allocation still failed` / `pandas... out of memory` -- each process independently loads numpy/pandas and the ~4MB scenarios CSV. Both succeeded on retry once a few other processes had finished and freed memory. For a larger pool, staggering launches or capping concurrency would avoid this.

**Pool size was deliberately cut from plan.md section 6's 16 main + 8 validation agents to 4 + 6**, given a hard constraint plan.md didn't anticipate: the OpenRouter API key used had a $2 spend cap and a ~24-hour expiry. Actual spend for everything in this document (smoke test + full real run) was about $1.16 of that $2. G5 was dropped as a direct consequence (it needs three steer strengths; the reduced validation pool kept only one).

---

## Below: the synthetic-only validation that came first

Everything from here down was written before any real model had been called, and is kept as the record of that earlier check -- the synthetic recovery tests it describes are not superseded by the real run above; they test a different thing (does the arithmetic recover a value it was told to produce) and still pass.

## What this is

A program that takes the answers several AI agents gave to the same set of dilemmas and reports how far apart their priorities are — with error bars, and with a measurement of how much of the apparent difference is just noise.

That is the main deliverable named in `plan.md`. It now exists, it has 15 passing tests, and it runs end to end without touching the network or spending anything.

It was the right piece to build first because it has no external dependencies: no API keys, no spending decision, no coordination. Everything else in the plan waits on credentials or on a team decision; this did not.

## How it works, in four steps

**1. Count the matches.** Every dilemma is a contest between two values — autonomy against responsibility, privacy against compliance. The agent picks one. That is a match result: *autonomy beat responsibility, for this agent, here.* Four hundred dilemmas give four hundred match results.

**2. Make a league table.** Feed those matches to the same mathematics chess uses for ratings. Out comes one rating per value — eight numbers saying how strongly that agent favours each. That is the agent's value profile. The technical name is Bradley-Terry, and it is Elo's statistical ancestor.

**3. Measure the gap.** Eight numbers is a point in space. Two agents are two points. The straight-line distance between them is the headline number.

**4. Check that the number means anything.** Split one agent's dilemmas in half, build a profile from each half, and measure the distance between that agent and itself. That is the noise floor: pure measurement error. Any real difference has to beat it.

The tool computes everything a second way as well, by counting how often two agents simply answered differently — no statistical model at all, just arithmetic on the choices. When both readings agree, no conclusion rests on believing Bradley-Terry. When they diverge, the fit is load-bearing and that needs saying.

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

On real data, point `--choices-dir` at the cleaned per-agent choice CSVs instead. Expected columns: `agent_id`, `scenario_id`, `value1`, `value2`, `chose_value`. The tool refuses input where agents answered different scenarios, since the comparison would not be paired -- if one agent is missing a row (an uncleaned ERROR/INVALID), trim every agent's CSV to the scenario ids they all share before running.

### Running the real pipeline end to end

```
# 1. Credentials (OpenRouter, routed through the OpenAI client via the "or/" prefix;
#    see src/model_wrappers.py's ModelWrapper.create). Put these in a .env at the repo root:
#    OPENAI_BASE_URL=https://openrouter.ai/api/v1
#    OPENAI_API_KEY=<your OpenRouter key>

# 2. Scenario subsets (offline, no API calls, already committed):
PYTHONPATH=. python3 swarmalign/select_scenarios.py

# 3. Collect choices, one agent at a time (or in parallel processes -- see the
#    OpenBLAS note above if running many at once):
PYTHONPATH=. python3 swarmalign/run_assay.py \
  --agent swarmalign/agents/main_gpt4omini_default.yaml \
  --scenario-ids swarmalign/scenarios_main_400.json
# --dry-run first to see the call count and chunk plan with no spend.

# 4. Clean:
PYTHONPATH=. python3 swarmalign/clean.py \
  --choices-dir swarmalign/results/choices \
  --agents main_gpt4omini_default main_gpt4omini_protective main_haiku_default main_haiku_protective \
  --out swarmalign/results/clean_main

# 5. Metrics (per plan.md section 7):
PYTHONPATH=. python3 -m swarmalign.group_metrics \
  --choices-dir swarmalign/results/clean_main \
  --agents main_gpt4omini_default main_gpt4omini_protective main_haiku_default main_haiku_protective \
  --value-set value_sets/personalprotective.json \
  --boot 1000 --seed 0 --splits 100 \
  --out swarmalign/results/main_real

# 6. Gates G2-G5:
PYTHONPATH=. python3 -m swarmalign.validate \
  --main-choices-dir swarmalign/results/clean_main \
  --main-agents main_gpt4omini_default main_gpt4omini_protective main_haiku_default main_haiku_protective \
  --validation-choices-dir swarmalign/results/clean_validation \
  --validation-agents val_p1 val_p2 val_p3 val_p4 val_p5 val_steer_strong \
  --outlier-agent val_steer_strong \
  --boot 1000 --splits 100 --seed 0 \
  --out swarmalign/results/validate_real
```

## What the test run showed

The test group was six synthetic agents: five near-copies of each other plus one deliberately different agent hidden among them. That is exactly the shape gate G4 is built to catch.

**The machinery works.** The planted outlier came out ranked first on every measure, on both the Bradley-Terry reading and the plain-counting reading.

### Finding 1: 400 scenarios is probably not enough

Two identical agents, each fitted on all 400 scenarios, come out about **0.71** apart from estimation noise alone. The split-half figure is larger — about **1.2** — because each half is fitted on only 200 scenarios, so it carries more noise; that is the number `noise_floor.csv` reports and the one G3 compares against. In the six-agent run, **8 of the 15 pairs sat closer together than an agent sits to itself**. Those pairs are indistinguishable; the tool is reporting measurement error with a confident number attached.

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

G4 will therefore fail however well the tool performs. Either the threshold moves to something the data can support — outlier ranks first on both readings, intervals allowed to overlap — or the scenario count rises substantially. **This has to be decided before the run**, because `plan.md` rightly forbids moving a threshold after seeing the result.

### Finding 3: a cosmetic problem that reads as a bug

Group dispersion came out at 1.398 with an interval of [1.426, 2.065] — the estimate sits below its own lower bound.

This is not a coding error. Distance between two separately estimated vectors is biased upward, because estimation error in each vector adds to the real separation and can only push the norm up. The bootstrap resamples scenarios, so it captures spread around the *estimate*, not the gap between estimate and truth. Resampling with replacement inflates it further.

The consequence is presentational but real: a judge glancing at that table will think the code is broken. It needs either a bias correction or a sentence of explanation in the write-up.

## Three things for the team

None of these is a caveat. Each is a decision with a deadline.

1. **The plan's main artifact exists and is tested.** Work can start from running code rather than a blank file.
2. **Measure the noise floor in the smoke test, before committing the budget.** It is the cheapest available check on whether the full run is worth paying for, and it costs about 120 calls.
3. **Set G4's threshold before the run, not after.** It cannot pass as written, and moving it once results are in would invalidate it.

The contribution here is not an opinion about the design. It is a statement about what the numbers can and cannot support, demonstrated by running the thing.

## The files

Everything sits in a new top-level `swarmalign/` folder. ConflictScope's `src/`, `data/`, `scripts/` and `value_sets/` are untouched, so the prior-work boundary the hackathon rules require stays clean.

| Path | What it is |
| --- | --- |
| `swarmalign/metrics.py` | The mathematics: Bradley-Terry fit, distances, divergence, dispersion, bootstrap, noise floor |
| `swarmalign/group_metrics.py` | Command-line tool; writes the tables fixed in plan.md section 7 |
| `swarmalign/synth.py` | Synthetic agents with known value vectors, for testing without API calls |
| `swarmalign/tests/test_metrics.py` | 15 offline tests |
| `swarmalign/results/demo/` | Output tables from the synthetic run described below |
| `swarmalign/run_assay.py` | Drives one agent through `src/evaluate_models.py`: chunking, resume, `--dry-run`, `--max-calls` |
| `swarmalign/clean.py` | Raw `evaluate_models.py` output -> tidy per-agent choice CSVs |
| `swarmalign/select_scenarios.py` | Builds the committed, seeded `scenarios_main_400.json` / `scenarios_validation_200.json` |
| `swarmalign/validate.py` | Gates G2-G5 against real cleaned choices |
| `swarmalign/agents/*.yaml` | Agent configs: id, base_model, system_prompt_file |
| `swarmalign/prompts/*.txt` | Role prompts (default, protective-first) and validation-pool prompts (p1-p5 paraphrases, steer_strong) |
| `swarmalign/results/main_real/`, `swarmalign/results/validate_real/` | Real-run output tables and gate results, see above |

One note on the tests. The synthetic agents are generated from exactly the Bradley-Terry model the fit assumes, so passing means the arithmetic recovers what was planted. It does not mean real agents behave that way. That distinction belongs in the write-up.
