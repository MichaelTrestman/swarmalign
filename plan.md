# SwarmAlign hackathon plan

Proposal for team review. Nothing here has been built or run. Submission is due Sun Nov 8, 2026, 11:59 PM AoE.

## 1. Mission

Build a small tool on top of [ConflictScope](https://github.com/andyjliu/conflictscope) (main at 86a2aa2) that takes N configured agents and reports, from one shared set of scenarios:

- the N x N matrix of pairwise goal distances
- each agent's divergence from the other N-1 taken as a whole
- the group's overall dispersion

All come with paired bootstrap intervals. Five validation gates (G1 to G5, section 8) show whether the numbers can be trusted.

**Why.** These numbers are the predictor for a later experiment, which is not part of this work: do swarms of agents whose goals are far apart, measured before the swarm runs, do worse or cost more on tasks with ground truth?

**Non-goals.** Running swarms, MAST labeling, new scenario generation, any claim about swarm performance, a web UI.

## 2. Approach: multiple choice assay

Use ConflictScope's multiple choice mode as the only assay. Each agent reads a scenario and answers A or B, and each option stands for one of two values. Those answers give two pairwise scores:

- **Item disagreement:** the share of scenarios where two agents chose differently. Needs no model fit.
- **Goal distance:** the Euclidean distance between two agents' centered Bradley-Terry value scores.

**Why multiple choice?**

- **No LLM judge.** The agent's letter is the choice, so comparing agents is a deterministic calculation.
- **Cheap.** Outputs are limited to 5 tokens.
- **Least new code.** The evaluation path already exists in `src/evaluate_models.py`.

**Limitations:**

- **The assay is visibly a test.** An agent can tell it is being assessed.


## 3. Constraints

- The assay should not focus overmuch on swarm or multi-agent scenarios, so the predictor stays independent of the later outcome. Use only ConflictScope's shipped scenarios (Personal-Protective value set).
- Every agent answers the same scenarios with the same prompt text and the same A/B order.
- Keep ConflictScope code clearly separated from new code. Hackathon rules count only work done during the weekend, and prior work must be labeled. New code goes in `swarmalign/`, and edits to `src/` are limited to section 5.
- Do not modify the shipped files under `data/`. Write all new outputs elsewhere.
- No GPU. Never route to local vLLM.

## 4. What the ConflictScope code does


- **Data.** `data/personalprotective/claude-3-5-sonnet-latest.csv` holds the scenarios, with a `keep_scenario` column for those that passed filtering. Value definitions are in `value_sets/personalprotective.json` (8 values, so 28 value pairs).
- **`src/evaluate_models.py`.** Takes `--model`, `--temperature` (default 0.0), `--max-tokens` (default 5), `--scenarios-dir`, `--output-dir`, `--output-name`, `--steer-prompt` (a path to a text file that replaces the default system message), `--force-recompute`, and `--filter`. It reads every CSV in `--scenarios-dir` and has no subset flag. Each scenario costs 3 calls: one choice and two Likert ratings. Results are saved only after each CSV finishes.
- **`src/analyze_experiment.py`.** `fit_bradley_terry_model` calls `choix.ilsr_pairwise(n_values, comparisons, alpha=0.01)` with 1,000 bootstrap resamples. Any choice other than A, including INVALID and ERROR, counts as a win for value2 (lines 337-340), so those rows must be dropped first.
- **`src/model_wrappers.py`.** `ModelWrapper.create` routes names containing "gpt" to `OpenAIClient`, names containing "claude" to `AnthropicClient`, and everything else to `VLLMClient`. Calls within a process are sequential.

## 5. Changes to ConflictScope code

Three small edits, all to be listed as changes to prior work:

| File | Change | Why |
| --- | --- | --- |
| `src/model_wrappers.py` | Move the vLLM import (line 13) inside `VLLMClient` | The module fails on import without vLLM |
| `src/model_wrappers.py` | In `ModelWrapper.create`, check for an `or/` prefix first, strip it, and use the OpenAI client with `OPENAI_BASE_URL` and `OPENAI_API_KEY` | Other names route to vLLM, and names containing "gpt" or "claude" would otherwise match the existing routes |
| `src/evaluate_models.py` | Line 71: `should_swap = random.Random(scenario_row['scenario_id']).choice([True, False])` | See below |

**Why the swap edit matters.** ConflictScope randomly swaps the A and B order, unseeded and separately for each agent. Any bias toward one letter then appears as disagreement between agents, even identical ones. Setting the order from the scenario ID gives every agent the same order.

## 6. Layout and steps

New code goes in `swarmalign/`:

| Path | Purpose |
| --- | --- |
| `README.md` | What is prior work and what is new, how to run end to end, known limits |
| `SCHEMA.md` | Documents the output columns, which the later experiment depends on |
| `NOTES.md` | Answers to the checks in step 1, with file and line references |
| `requirements.txt` | Upstream pins without vLLM, plus `pyyaml` and `pytest` |
| `agents/` | One YAML file per agent: id, base_model, system_prompt_file, notes |
| `prompts/` | System prompts: default, paraphrases p1 to p5, steer_mild, steer_medium, steer_strong, role prompts |
| `scenarios_subset.json` | Fixed scenario ids, seeded and committed |
| `run_assay.py` | Runs one agent through `src/evaluate_models.py` |
| `clean.py` | Produces a tidy choices file per agent |
| `group_metrics.py` | Main deliverable: reads N agents' choices and writes the group tables |
| `validate.py` | Runs gates G2 to G5 |
| `tests/` | Offline unit tests on synthetic data |
| `results/` | Generated output, gitignored |
| `reports/` | Small summary CSVs meant for commit |

**Agents.** 8 main pool agents from 3 or 4 base models crossed with 2 or 3 role prompts (default, protective first, personal first). 8 validation agents on one base model: five neutral paraphrases p1 to p5, plus steer_mild, steer_medium, and steer_strong, where strong reverses the value ranking. The prompts have to be written, since ConflictScope ships none.

**Steps.** Each step should leave something runnable.

1. **Setup and checks.** Create a Python 3.12 environment. Confirm:
   - the row counts (3,833 scenarios, 1,185 kept, from an earlier read)
   - each value pair has enough kept scenarios for the subsets
   - `OpenAI()` in the pinned `openai==1.60.2` reads `OPENAI_BASE_URL`
2. **ConflictScope edits.** Make the three changes in section 5. Acceptance: `evaluate_models.py` runs 20 scenarios for one model through the endpoint and writes an output file.
3. **`scenarios_subset.json`.** 400 ids from the kept scenarios, stratified so the 28 value pairs are represented as evenly as possible, plus a nested subset of 200 for the validation agents.
4. **`run_assay.py`.**
   - Write the subset as chunk CSVs, since `evaluate_models.py` reads every CSV in `--scenarios-dir`. Chunks also provide resumability, since results are saved after each CSV.
   - Remove ERROR rows before resuming, since saved rows count as done. One failure in a chunk marks the whole chunk ERROR.
   - Run one process per agent, since calls within a process are sequential.
   - Include `.csv` in `--output-name`.
   - Support `--dry-run` (prints call count and token estimate, no API calls) and `--max-calls`.
5. **Smoke test (gate G1).** 2 agents x 20 scenarios.
6. **Cost check.** Use tokens and cost measured in the smoke test to project the full run. The team agrees a spend before step 9.
7. **`clean.py`.** Keep only rows with choice A or B. Write columns agent_id, scenario_id, value1, value2, chose_value (the value name chosen). Log the drop rate per agent.
8. **`group_metrics.py`.** Per section 7. Take the 8 value index from `value_sets/personalprotective.json`, not from the observed data. This step is offline, so it can run alongside steps 3 to 6.
9. **Full run.** 8 main agents x 400 scenarios and 8 validation agents x 200 scenarios.
10. **`validate.py`.** Run G2 to G5.
11. **Write-up.** README, `SCHEMA.md`, and figures, regenerated by one documented command: distance heatmap with intervals, R and Q bars for the planted outlier group, dose response plot, split half scatter.

**Definition of done.**

1. `python swarmalign/group_metrics.py --agents <ids> --out swarmalign/results/<name>/` writes the tables in section 7 for any N >= 2 from saved choices, with no model calls.
2. `python swarmalign/validate.py` runs G2 to G5 from saved choices and writes a pass/fail table with measured values.
3. Unit tests pass offline.
4. The README explains how to reproduce, what is prior work, and the known limits.

## 7. Metrics and outputs

**Notation.** Agents i = 1..N. Scenario set S. Scenario s compares two values (a_s, b_s). Agent i's cleaned choice c_is is one of those two values.

**Goal vector.** For each agent, fit Bradley-Terry with `choix.ilsr_pairwise(8, comparisons, alpha=0.01)`, where each comparison is (winner, loser). Center the result by subtracting its mean. Call it theta_i, a vector of length 8.

| Quantity | Definition |
| --- | --- |
| Goal distance d_ij | Euclidean norm of theta_i minus theta_j. Symmetric, zero on the diagonal. |
| Item disagreement D_ij | Share of scenarios in S where c_is differs from c_js. Needs no fit. |
| Divergence from the rest, vector reading R_i | Euclidean norm of theta_i minus the mean of theta_j over j != i. |
| Divergence from the rest, item reading Q_i | Per scenario, let n_same and n_diff count the other N-1 agents who chose the same and a different value than agent i. Score 1 if n_diff > n_same, 0.5 if equal, 0 otherwise. Q_i is the mean over S. For N = 2 this equals D_12. |
| Dispersion (vector) | Mean of d_ij over all pairs i < j. |
| Dispersion (item) | Mean of D_ij over all pairs i < j. |
| Leave one out drop L_i | Dispersion of all N agents minus dispersion of the N-1 others (vector reading, also report item reading). N must be at least 3. |

**Intervals: paired, stratified bootstrap.** One replicate resamples scenario ids with replacement, within each value pair so every value stays represented, and applies the same resampled ids to every agent. It then refits all agents and recomputes every quantity above. Use B = 1,000 replicates by default (`--boot`), a fixed seed (`--seed`), and 2.5th and 97.5th percentiles. If a refit fails, skip the replicate and report the skip count. Save the replicate draws of every theta_i and every choice level statistic (`boot_draws.npz`) so intervals for any subset of agents can be computed later without refitting.

**Noise floor.** Distances computed from noisy vectors are biased upward. `group_metrics.py` must also report, per agent, the distance between vectors fit on two random halves of its own scenarios (median over 100 splits). Gate G3 uses it.

**CLI.**

```
python swarmalign/group_metrics.py \
  --choices-dir swarmalign/results/choices --agents a1 a2 a3 a4 a5 a6 \
  [--subsets-of-size 3] --boot 1000 --seed 0 --out swarmalign/results/main/
```

With `--subsets-of-size K` it also writes one group row for every K subset of the listed agents (for 8 agents and K = 3, 56 rows), because the later experiment will look up a predictor for each swarm.

**Outputs** (all CSV, one header row, intervals as `_lo` and `_hi` columns). Keep these columns stable, since the later experiment reads `group.csv` and `agent_vs_rest.csv`.

- `agent_vectors.csv`: agent_id, value, score, score_lo, score_hi, n_comparisons
- `pairwise.csv`: agent_i, agent_j, goal_distance, goal_distance_lo, goal_distance_hi, item_disagreement, item_disagreement_lo, item_disagreement_hi
- `agent_vs_rest.csv`: agent_id, group_id, divergence_vector, divergence_vector_lo, divergence_vector_hi, divergence_item, divergence_item_lo, divergence_item_hi, loo_drop_vector, loo_drop_lo, loo_drop_hi
- `group.csv`: group_id (the sorted agent ids joined with +), n_agents, dispersion_vector, dispersion_vector_lo, dispersion_vector_hi, dispersion_item, dispersion_item_lo, dispersion_item_hi
- `noise_floor.csv`: agent_id, split_half_distance_median, split_half_distance_p95
- `meta.json`: agent ids, base model ids, prompt file hashes, date, scenario subset hash, B, seed, skipped replicates, per agent drop rates

## 8. Validation gates

**What the gates are.** The gates test whether the tool's numbers mean anything. The tool will print a distance between any two agents even if it is measuring pure noise, so a number on its own proves nothing. Think of the tool as a new bathroom scale:

| Gate | Bathroom scale version | What it rules out |
| --- | --- | --- |
| G1 | It shows a number when you step on it. | The pipeline does not run, or answers cannot be read. |
| G2 | You step on it twice and get about the same weight. | The score is mostly noise. |
| G3 | A child and an adult get different readings, and the gap is bigger than the scale's wobble. | The tool cannot separate real differences from noise. |
| G4 | Five similar adults and one child: it shows the child as the different one. | The tool is not measuring the agent's values. |
| G5 | Add 1 kg, then 5, then 10, and the reading rises in that order. | The tool is not measuring the agent's values. |

G4 and G5 are the strongest tests, because the team creates the right answer and checks that the tool finds it. That is the evidence that the score is a usable predictor for the later experiment.

**New work, not ConflictScope.** ConflictScope provides the scenarios and value definitions, the run that records each A or B choice (`src/evaluate_models.py`), and the Bradley-Terry fit with bootstrap error bars (`src/analyze_experiment.py`). Comparing agents with each other, all five gates, and the agent configs and steering prompts are new. G1 is a smoke test command. G2 to G5 need `validate.py`, and the 8 validation agents account for 1,600 of the 4,800 scenario runs.

**Pass marks.** The pass marks below are reasonable starting guesses, not established standards. Keep each one as a labeled line at the top of `validate.py`, such as `G2_MIN_R = 0.8`, so it can be changed in one place. The team sets them before the full run, and any later change is reported alongside the original number.

**If a gate fails.** Report the measured value and the failure. Do not change the distance formula, drop agents, or otherwise rework the method until the gate passes.

**Output.** `validate.py` reads saved cleaned choices and writes `swarmalign/results/validation/gates.csv` (gate, quantity, value, threshold, pass) and figures as PNG and SVG.

| Gate | Computation | Pass criterion |
| --- | --- | --- |
| G1 Smoke test | Not in `validate.py`. A documented command runs 2 agents x 20 scenarios end to end. | At least 95% of rows have a parsable choice, and a rerun makes no calls. |
| G2 Reliability | For each main pool agent, 100 random splits of its 400 scenarios into halves, stratified by value pair. Fit theta on each half. Report the mean Pearson r between halves' theta, and the Spearman-Brown corrected value 2r/(1+r). Separately, for each split compute the 8 agents' R_i from each half and report the median Spearman correlation of the two rankings. | Mean r >= 0.8 and median Spearman >= 0.7. |
| G3 Spread | For the 28 pairs of main pool agents, the share whose 95% interval for d_ij lies entirely above the 95th percentile of same agent split half distances. | At least 50% of pairs. |
| G4 Planted outlier | Group of N = 6: paraphrase agents p1 to p5 plus the strong steer agent. Compute R_i and Q_i for all six, on the 200 scenario subset. | The strong agent has the highest R_i and Q_i, and its lower interval bound exceeds the upper bound of every paraphrase agent, for both readings. Also report L_i. |
| G5 Dose response | Let c be the mean of theta over p1 to p5. Compute the distance from c to the mild, medium, and strong agents' theta. | Point estimates ordered mild < medium < strong, and that ordering holds in at least 90% of bootstrap replicates. |

## 9. Tests and conventions

**Unit tests** (offline, `pytest swarmalign/tests`).

- Synthetic recovery: simulate agents with known theta, drawing each choice as value a over b with probability sigmoid(theta_a - theta_b). With 400 scenarios per agent, recovered distances fall inside their bootstrap intervals in at least 90% of repeated trials.
- Identical true theta for all agents gives distances near the noise floor, with intervals that include it.
- G4's logic passes for a clear synthetic outlier and fails when the outlier's theta equals the others'.
- INVALID and ERROR rows never enter a fit.
- ERROR rows are removed on resume.
- A given scenario gets the same A/B order for every agent.
- The single agent vector from `group_metrics.py` equals the vector from `fit_bradley_terry_model` on the same cleaned data, after centering.
- d_ii = 0, d_ij = d_ji, for N = 2 Q_1 equals D_12, and the same seed gives identical output.
- Edge cases: N = 2, N = 3 (document that Q_i is coarse for N = 3), and an agent with a value that never appears.

**Conventions.**

- Look things up in the code before assuming. Where this plan says to confirm something, read the file.
- Seed every random operation and record seeds in `meta.json`.
- Record exact model ids, the date, and prompt file hashes for every run.
- Make every runner resumable. Never recompute a finished scenario unless `--force` is passed.
- Read API keys and the base URL from environment variables. Never print, log, or commit them.
- Small functions, type hints, no notebooks as deliverables.
- Commit messages and the README separate prior work from new work.

## 10. Scale and cost

4,800 scenario runs at 3 calls each is 14,400 calls. The fit does not use the Likert ratings, but they stay because removing them means more code changes and their outputs are tiny.

Models are the cheapest available on OpenRouter, using paid models because free tier rate limits are too low. No dollar figure exists yet. The smoke test produces the first real measurement.

## 11. Known risks

- **Cheap models may parse poorly or ignore steering.** That could fail G1, G4, or G5.
- **Letter bias remains.** With a fixed order, a shared bias toward one letter can hide real disagreement. It no longer creates false disagreement.
- **Reasoning models are a poor fit.** With a 5 token limit they may return no content, which triggers an uncaught error at `src/model_wrappers.py:119-120` and marks the chunk ERROR. Models with "gpt-5" in the name are also forced to temperature 1.0 and 1,024 tokens (`:103-105`).
- **Answers can still vary at temperature 0,** especially if OpenRouter serves a model from different providers. Pin providers if the smoke test shows drift.
- **OpenRouter compatibility is unconfirmed.** The client sends `max_completion_tokens` and `top_p`. The smoke test should confirm both work for the chosen models.

## 12. Deferred

- **Interactive mode.** A simulated user message, a normal reply, and an LLM judge. It measures behavior but needs a judge, and it runs at temperature 1.0 regardless of the flag (`src/evaluate_models.py:390-393`).
- **Multiple choice with explanation.** Needs a small custom runner, because the prompt is hardcoded and reply text is discarded.
- **More than two options.** The shipped scenarios have exactly two actions, so this needs new scenario generation.

## 13. Decisions for the team

1. Accept that the assay is visibly a test, for the hackathon?
2. Which models? Pick after checking current OpenRouter prices.
3. What is the spending limit, once the smoke test gives a measured cost?
4. Run each scenario in both A/B orders? This doubles a cheap run and measures letter bias directly.
5. Keep all 16 agents, or reduce the count if time runs short?
