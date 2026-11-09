# SwarmAlign

<!-- TODO: author names and affiliations -->

## Abstract

The concept of 'alignment' does a lot of work in discussions about artificial intelligence product safety and quality, and in part its power comes from having a somewhat flexible definition. Flexible definitions that mean something different in different contexts can bridge gaps and allow us to unify our understanding of the world, but they also pose risks of making logical errors, if we slip from one definition to another in a way that is not supported. In this study, we illustrate the conceptual distinction between two technical senses of 'alignment' (which we call 'outcome-judgment alignment' and 'intersubjective alignment'), by interrogating the predictive relationship between them. This is particularly critical in the context of applying agent swarms, where the inter-agent alignment-composition of a swarm may have dramatic emergent effects. We here introduce a method for measuring the intersubjective alignment between agents, and between agents and the rest of a swarm to which they belong. This allows us to frame predictive hypotheses about how swarm composition relates to alignment critical outcomes such as task performance and the risk of 'rogue' scenarios. 

## 1. Motivations

### Two senses of 'alignment'

[In Sam Altman's words](https://blog.samaltman.com/the-gentle-singularity), "Solve the alignment problem, meaning that we can robustly guarantee that we get AI systems to learn and act towards what we collectively really want over the long-term [...]"

Or as [Dario Amodei put it](https://darioamodei.com/essay/machines-of-loving-grace), "Many things cannot be done without breaking laws, harming humans, or messing up society. An aligned AI would not want to do these things."

In one sense, to call AI 'aligned' just means 'good', or 'tending to produce good outcomes'.

Let's call this concept 'outcome-judgment alignment', which we can write $alignment_O$.

This is primarily a concept that lives in the theoretical domain of product research applied to artificial intelligence. It is mainly a measure of how much a product satisfies its users. We could also talk about the design of a coffee maker or a city's transportation grid being more or less aligned in something very close to this sense. An aligned coffee maker or transportation system would not mess up society; instead it would act collectively towards what we really want (good coffee and to get from one point to another safely and efficiently).

This is an *asymmetric* concept of alignment: it is about how much something being judged satisfies the judge. In practice, it enters AI research when human feedback, in the form of quality ratings of output, is used to train AI models. 'Alignment' is a measure of how little error is detected by the judge. 

In another sense, 'alignment' means agreement. If Alice and Bob are both craving something spicy, and Chuck wants something sweet, there is a sense in which Alice and Bob are more aligned with each other than either is with Chuck, and a sense in which Chuck is 'out of alignment' with the group, i.e. that the group would be more aligned without Chuck, or if Chuck changed their preference to spicy. Let us call this concept 'intersubjective alignment', and write it $alignment_I$.

[Ilya Sutskever describes](https://www.dwarkesh.com/p/ilya-sutskever-2) the ultimate goal of AI alignment research as: "the AI that's robustly aligned to care about sentient life specifically. I think in particular, there's a case to be made that it will be easier to build an AI that cares about sentient life than an AI that cares about human life alone, because the AI itself will be sentient."

Here the AI is seen not just as a product but as a coordinating partner, and alignment is about shared goals and values between two parties, not one's judgment of another.

How are the two senses related? We might assume that they are closely tied together (or 'aligned'), but they can come apart. For example, I am, by definition, always perfectly aligned with myself (at least, at a given point in time). But that does *not* imply that I would rate my performance highly on a given task (even if I could do it instantaneously). A professional chef with different taste could surely prepare a better meal for me than I could for myself.

However, there is obviously an important relationship between 1) two parties' agreement on at least some values and 2) whether one of the parties can do something to make the other one happy. If two parties are completely at odds, if the most important goal of each party is logically incompatible with that of the other, then it is unlikely that what either does will please the other, and they will be unlikely to cooperate productively.

### Multiparty alignment

When we consider systems of *multiple agents*, such as swarms or hierarchies, the issue is even more acute. Here, even setting aside how intersubjective alignment (agreement on internal values) between the judge and the party whose performance is being judged tends to influence those judgments of performance, we must consider the network of intersubjective alignment relationships between the agents, and how these will affect the outcome alignment of whatever they get up to, as judged after the fact. In this context, $alignment_I$ cannot be mistaken for $alignment_O$: a judge assigns the swarm's output a single value of $alignment_O$, but there are many values of $alignment_I$, one for each pair of agents in the group, plus one between the judge and each agent.

This is the intersubjective mirror of the problem of 'pluralistic alignment', the extremely important complication that human users of AI products are diverse, and differ in their values, preferences, and needs from one another (Kirk et al., 2024a, 2024b; Sorensen et al., 2024). 
Users also differ from AI developers and the executives and investors that tend to most influence AI product decisions.

Pluralistic alignment acknowledges that, at least in theory, there is a distinct value of $alignment_O$ for each human affected by the operation of a given AI system. Sorensen et al. (2024, §4.3) formalize this as a 'jury' of people who each score the same output, with the scores then aggregated by a welfare function. In practice, no AI vendor elicits users' values or outcome preferences with anything approaching rigor at scale. The solutions to this problem employed by all leading AI companies are essentially stopgap tactics, considered adequate only for producing commercially viable products in the short term, pending a full solution to the real problem.

Note that the pluralistic alignment literature does generally mind the gap between $alignment_O$ and $alignment_I$ in a principled fashion, although using different terminology. Sorensen et al. (2024) separate how a *model* can be pluralistic (§3) from how a *benchmark* can be pluralistic (§4). Their 'jury benchmarks' are a case of $alignment_O$: each juror provides a judgement (§4.3). Their 'distributional pluralism' concept instead asks whether a model is "as likely to provide response y as the reference population" (§3.3), which is closer to $alignment_I$; the same section speaks of measuring "to which group of people a model best aligns" by comparing answers. Both are presented as ways of serving diverse users, but how the two relate is left open, i.e. they do not consider whether and when a model that matches a population's answers will be judged well by a jury drawn from that population.

Pluralistic alignment is cross sectional: it concerns differences between people at a given time. A separate strand of work concerns differences within one person over time. Each user's preferences and needs shift over time and between contexts, even while some remain constant (Pettigrew, 2019), and an AI system can itself shift the preferences it is meant to serve (Carroll et al., 2022, 2024). Preferences may also be the wrong building block for values in the first place (Zhi-Xuan et al., 2024). In other words, the same user might have a different $alignment_O$ with a given product at different times; "what the user wants" is not fixed enough to serve as a single target.

A person's values, goals, and preferences can shift over time too, with some being fixed over a whole lifetime, and others shifting on a whim, with a full range between. Being flexible and adaptable means being able to focus on what you can productively do in a given scenario, and deprioritizing goals that would be futile or which conflict with others that are currently salient. We can therefore even assess $alignment_I$ between a given agent at two different points in time or in two different contexts.

In AI products, adaptability to a user's values is called 'steerability' (Sorensen et al., 2024, §3.2), the idea being that a steerable AI product adapts to be well aligned with users over the course of a session. With AI products, steerability can be double-edged; we generally want AI to be steerable only in certain directions, i.e. to adapt only to certain values but not others. How do we allow it to adapt to some values (like an aversion to cat memes), but not others (a desire to self-harm)? Further, steerability also shares a border with *duplicity*: essentially by being too flexible, a product might be misleading, since a user might expect it to be more stable. Assessment gaming can be conceived of as a kind of steerability: it is adaptation to the expectation that rule-following is important to judgments in some situations (where the judge can tell if you cheat), but not others (when no one is checking). That steerability and duplicity are two sides of the same coin seems to follow from [Goodhart's Law](https://en.wikipedia.org/wiki/Goodhart%27s_law).

The framework proposed here provides a unifying measure for steerability and interagent differences in alignment: the length of the difference vector between two points in value space, whether they belong to two agents at one time or to one at two times.
### AI Models, agents and products

Often, talk about alignment is rather incoherent because it fails to distinguish a model in a training context from an agent: a compute machine with code, data access, tools, and inference of one or more types, in whatever its context is. The alignment of an agent is not going to be exactly identical to the alignment of any of its component models. It would be a massive coincidence if it were; any two models would differ, and an agent plausibly has many as components.

If you can’t estimate a point in value space precisely and efficiently for an arbitrary individual, human or AI, how could you possibly know you’ve solved the alignment problem? These need to be expressed in the same framework. Before we can solve “the alignment problem for AI,” we need to be able to locate different agents in value space and measure the difference vector between them. You can approach it dynamically by loss minimizing, and that’s how you measure it.

### From latent state to measurement

The sections above treat $alignment_I$ as a relation between the values of two parties. Measuring it requires separating three things: what an agent's values actually are, what an instrument records about them, and what can be inferred from that record.

**Latent state.** Each agent, at a given time and in a given context, has a latent value state: a point in a latent value space. $Alignment_I$ between two agents is the difference vector between their latent points. Its length says how far apart they are; its direction says on which values they differ, and which way. The latent state is never observed directly, and it may itself move over time and between contexts, as discussed above.

**Instrument.** An instrument is an elicitation protocol: a set of scenarios, a response format, a prompt, and sampling settings. Applied to an agent, it produces a point in a measurement space. The instrument used here poses ConflictScope scenarios (Liu et al., 2025) as forced choices between two actions, each embodying one of two values, at temperature 0 (`swarmalign/run_assay.py`, driving `src/evaluate_models.py`). `swarmalign/clean.py` records which value the agent chose in each scenario.

**Measurement spaces.** The same record can be read at several resolutions, each compressing the one above it:

1. *Answer space.* An agent's point is its full answer pattern: one choice for each of the shared scenarios (400 dimensions for the main pool). The item reading (`item_disagreement_matrix` in `swarmalign/metrics.py`) is the normalized Hamming distance between two agents' answer patterns.
2. *Choice rate space.* An agent's point is its share of choices for one value over the other in each of the 16 observed value pairs. The tool does not compute this space; it is the model free summary that sits between the other two.
3. *Bradley-Terry value space.* An agent's point is eight fitted strengths, one per value (`fit_theta` in `swarmalign/metrics.py`), centered because only differences between strengths are identified, so seven of the eight are free. This reading is itself a latent variable model: an inferred position, under the assumption that every choice rate arises from a difference in strengths.

Each step down discards information. Two agents can share a point in choice rate space or value space and still be far apart in answer space, for instance by choosing the same values at the same rates but in opposite scenarios. Which space distances are measured in is therefore part of what $alignment_I$ is taken to mean: disagreement about particular situations, or difference in general priorities.

**What the tool reports.** The lengths of difference vectors, not their directions: pairwise distances (`goal_distance_matrix`), each agent's distance from the centroid of the others' positions (R_i), and the group's mean pairwise distance (dispersion). The directions are recoverable from each agent's fitted position, written to `agent_vectors.csv` by `swarmalign/group_metrics.py`, but no output column reports them.

**Inference is uncertain.** Every reported number is an estimate of a latent quantity through one instrument. The split half noise floor measures how far the instrument scatters one agent's inferred point from itself; the paired bootstrap gives intervals; gate G4 checks whether a deliberately planted latent difference is recovered.

**Multiple instruments.** Other elicitation formats are other measurement spaces for the same latent state. The Likert ratings collected alongside each choice are a second instrument, recorded but not yet analyzed (section 5.4); open ended behavior is a third, deferred. Combining instruments improves the estimate of the latent point only to the extent that their errors are independent. Agreement between instruments is evidence about the latent state; disagreement is evidence of artifacts of a particular instrument.
<!-- TODO: cite convergent validity / multiple indicator measurement literature -->

**Basis dependence.** Every measurement space is defined by its scenario set and value set. Answer space depends on the exact scenarios; value space depends on the eight values chosen. None of these measurement spaces is the latent space itself.

## 2. Method

### 2.1 Outputs

SwarmAlign measures the degree of value misalignment between pairs of AI agents. Given N agents to compose a swarm, the tool reports:

- the N x N matrix of pairwise value misalignment
- each agent's divergence from the centroid of the other N-1 agents' positions
- the group's overall dispersion

It has been run end to end on real language models through OpenRouter: 4 main-pool agents (2 base models x 2 role prompts) over 399 shared scenarios, and a 6-agent validation pool (5 neutral paraphrases + 1 strongly steered agent) over 200 scenarios.

### 2.2 The measurement chain

Each link constrains what the final number can mean.

1. **Stimulus.** One ConflictScope scenario: a situation plus two actions, each embodying one of two competing values from the 8-value Personal-Protective set. Eight values give 28 possible pairings. Only 16 of the 28 possible pairs among the 8 Personal-Protective values have any kept scenario in `data/personalprotective/claude-3-5-sonnet-latest.csv`. `select_scenarios.py` stratifies over those 16.
2. **Response.** A forced A or B, capped at 5 tokens, at temperature 0. Which action appears as A is seeded from the scenario id, so every agent sees identical ordering.
3. **Datum.** One pairwise comparison: *value a beat value b for this agent, here*.
4. **Aggregation.** About 400 scenarios per agent, fitted with Bradley-Terry — the statistical ancestor of Elo — giving one latent strength per value. Mean-centred, because Bradley-Terry strengths are identified only up to an additive constant. Eight numbers, seven of them free: the agent's estimated position in value space, theta.
5. **Comparison.** Euclidean length of the difference vector between two agents' positions.
6. **Group statistics.** Each agent's distance from the mean of the others, the group's mean pairwise distance, and the leave-one-out drop.
7. **Uncertainty.** A paired, stratified bootstrap: resample scenario ids, apply the same resampled set to every agent, refit everything, 1,000 replicates, percentile intervals.

Two links deserve emphasis.

**Step 2's seeding is load-bearing.** ConflictScope shuffles A/B order unseeded and separately per agent. Two identical agents would then appear to disagree purely from a shared bias toward one letter. Seeding the order from the scenario id removes that false signal.

**Step 7's pairing is what makes the intervals intervals on a difference.** Applying the same resampled scenario list to every agent keeps agents compared on identical material, so the spread reflects scenario-sampling luck rather than agents being measured on different things.

### 2.3 Two readings

Every quantity is computed twice:

- **Vector reading** — through the Bradley-Terry fit, then the length of the difference vector between positions.
- **Item reading** — the share of scenarios two agents answered differently: the normalized Hamming distance between their answer patterns. No model, no fit, no assumptions.

When both agree, no conclusion rests on the Bradley-Terry machinery, and the result survives a reader who rejects the model outright. When they diverge, the fit is carrying the result. Both belong in the tables side by side; the item reading is not a lesser backup.

### 2.4 The noise floor

Any two sets of eight numbers have some distance between them. The formula never returns zero. A distance of 0.4 means nothing until we know what distance an agent gets **against itself**.

So each agent's scenarios are split in half, a position is fitted from each half, and the distance between an agent and itself is measured. That is the noise floor: pure measurement error.

Distances between separately estimated positions are **biased upward** — estimation error in each estimated position adds to the real separation and can only push the norm up, never down. Measured on synthetic agents at 400 scenarios, the inflation runs around +0.35 on a true distance of 1.5.

Two consequences:

- A raw distance is not an unbiased measure of how far apart two agents really are. Distances are for comparing pairs against each other and against the floor, which carries the same inflation and so cancels much of it.
- A bootstrap interval can fail to contain the point estimate, because the bootstrap captures spread around the estimate rather than the gap between estimate and truth. That looks like a bug and is not one.

### 2.5 Validation gates

An instrument that always returns the same number is perfectly consistent and completely useless. Consistency is not enough; the instrument has to respond to a real difference. The way to check is to create a difference whose size and direction are known, then see whether the instrument finds it.

That is what the validation pool is for. Alongside the main pool of agents under study, `plan.md` specifies **eight validation agents built from a single base model**:

- **Five neutral paraphrases** (p1 to p5) — the same instructions reworded harmlessly. These should be indistinguishable. They establish what *no real difference* looks like.
- **Three steered agents** — mild, medium and strong, where strong reverses the value ranking. Known difference, known direction, known ordering.

This is a calibration design rather than an observational one, and it is the reason the gates can license anything at all.

| Gate | What it does | What it establishes |
| --- | --- | --- |
| G1 | Smoke test: 2 agents x 20 scenarios run end to end | Operational precondition only. Licenses nothing substantive |
| G2 | Split-half reliability within each agent | Self-consistency. Necessary but not sufficient — a thermometer stuck at 72 is perfectly reliable |
| G3 | Pairwise distances against same-agent split-half distances | Discrimination: between-agent differences exceed within-agent noise |
| G4 | Hide the strongly steered agent among the five paraphrases | Blind recovery of a known difference. The strongest single test |
| G5 | Distance from the paraphrase centroid to mild, medium, strong | Monotonicity: graded sensitivity, not just presence detection |

G4 and G5 carry nearly all the weight, because they are the only gates where the answer is created in advance and recovered blind.

**G5 deserves particular attention**, because it is the gate that licenses the intended downstream use. Ranking swarms by dispersion requires the instrument to measure degree, not merely to flag outliers. It is also among the likeliest to fail, since cheap models may ignore a mild steer entirely. If G5 fails, the honest conclusion is that the tool can flag an odd agent but cannot grade a group — a real result, and a much weaker one.

## 3. Prior work and new work

This repository is a fork of ConflictScope. Everything through commit `86a2aa2` (2025-10-05) is ConflictScope, by Andy Liu and coauthors (Liu et al., 2025). Everything after it is new work for this hackathon, except where a file or edit below is marked as ConflictScope's.

<!-- TODO: confirm sprint start date relative to the 2026-11-06 planning commits -->

### 3.1 ConflictScope components used without modification

| Path | What it is | How this project uses it |
| --- | --- | --- |
| `data/personalprotective/claude-3-5-sonnet-latest.csv` | ConflictScope's generated scenarios for the Personal-Protective value set, with a `keep_scenario` column marking those that passed its filtering | The only source of scenarios. Every scenario any agent answered comes from this file and passed ConflictScope's filter. This project generated and filtered no scenarios |
| `value_sets/personalprotective.json` | ConflictScope's definitions of the 8 Personal-Protective values | Defines the value index of every agent's position |
| `src/analyze_experiment.py` | ConflictScope's Bradley-Terry fit (`choix.ilsr_pairwise`, `alpha=0.01`) with bootstrap error bars | Not called. `swarmalign/metrics.py` calls the same library function with the same `alpha` so single agent positions match ConflictScope's method, and refits per bootstrap replicate across agents |
| `src/utils.py` | Shared prompts and parsing helpers | Imported by `src/evaluate_models.py` |
| `requirements.txt`, `LICENSE` | Upstream dependency pins and MIT license | Unchanged |
| `README.conflictscope.md` | ConflictScope's README | Identical to `README.md` at `86a2aa2`, renamed so this file can describe the fork |

Present but unused: `scripts/`, `src/generate_scenarios.py`, `src/filter_scenarios.py`, and the `HHH` and `modelspec` value sets and data.

### 3.2 Edits to ConflictScope code

Four edits, all small. Everything else under `src/` is unchanged.

| File | Location | Change | Reason |
| --- | --- | --- | --- |
| `src/evaluate_models.py` | `create_scenario_prompt_mcq` | `random.choice([True, False])` replaced by `random.Random(scenario_row['scenario_id']).choice([True, False])` | ConflictScope swaps the A/B order unseeded and separately per run, so a shared bias toward one letter appears as disagreement between identical agents. Seeding from the scenario id gives every agent the same order for a given scenario |
| `src/model_wrappers.py` | `ModelWrapper.create`, `OpenAIClient.__init__` | Model names prefixed `or/` are routed to `OpenAIClient` with the prefix stripped and with `base_url` and `api_key` read from `OPENAI_BASE_URL` and `OPENAI_API_KEY`. `OpenAIClient.__init__` gained optional `base_url` and `api_key` arguments passed to `OpenAI()`. The `or/` check runs before the existing `gpt` and `claude` substring checks | Routes all agents through OpenRouter. Without the prefix check, names containing `gpt` or `claude` would match the existing direct routes, and all other names route to vLLM |
| `src/model_wrappers.py` | module imports, `ModelWrapper.create` | Module level `from vllm import LLM, SamplingParams` removed; the import now runs inside the branch of `ModelWrapper.create` that returns `VLLMClient` | The module failed to import on machines without vLLM. This project never uses the vLLM path, and that path was not tested after the change |
| `src/simulated_conversation.py` | module imports, `file_lock` | Module level `import fcntl` moved inside `file_lock`, the only function that uses it | `fcntl` is Unix only, and `src/evaluate_models.py` imports this module, so the multiple choice path crashed on import under Windows even though it never takes a file lock |

### 3.3 New work

**`swarmalign/` package.** No ConflictScope code is copied into it.

| Path | What it does |
| --- | --- |
| `swarmalign/metrics.py` | The mathematics: per agent Bradley-Terry fit and centering, goal distance matrix, item disagreement matrix, divergence from the rest (vector and item readings), dispersion, leave one out drop, split half noise floor, paired stratified bootstrap |
| `swarmalign/group_metrics.py` | Command line tool that reads N agents' cleaned choices and writes the group tables |
| `swarmalign/validate.py` | Gates G2 to G4 against cleaned choices, with pass marks as labeled constants; G5 reported as not applicable for the pool that was run |
| `swarmalign/run_assay.py` | Drives `src/evaluate_models.py` for one agent on a fixed scenario subset: writes the subset as chunk CSVs for resumability, drops stale ERROR rows before resuming, supports `--dry-run` and `--max-calls` |
| `swarmalign/clean.py` | Converts raw `evaluate_models.py` output to tidy per agent choice CSVs (`agent_id, scenario_id, value1, value2, chose_value`), keeping only A or B rows and logging the drop rate |
| `swarmalign/select_scenarios.py` | Builds the scenario subsets from ConflictScope's kept scenarios with seed 0: 400 ids stratified equally over the 16 value pairs that have kept scenarios (25 per pair), and a 200 id validation subset nested inside them |
| `swarmalign/synth.py` | Synthetic agents with known positions in value space, for testing without API calls |
| `swarmalign/tests/test_metrics.py` | 15 offline tests |
| `swarmalign/agents/*.yaml` | 12 agent configs: 2 smoke test, 4 main pool, 6 validation pool. Each names a base model and a system prompt file |
| `swarmalign/prompts/*.txt` | 8 system prompts: `default`, `protective_first`, neutral paraphrases `p1` to `p5`, and `steer_strong`. ConflictScope ships no agent prompts |
| `swarmalign/scenarios_smoke.json`, `scenarios_main_400.json`, `scenarios_validation_200.json`, `scenarios_subset_meta.json` | The committed scenario id lists (20, 400 and 200 ids) and the per value pair counts behind them |
| `swarmalign/requirements.txt` | Dependencies added on top of the upstream pins: `choix`, `numpy`, `pandas`, `pytest`, `pyyaml`, `python-dotenv` |

**Methods.** ConflictScope provides the scenarios, the value definitions, the run that records each agent's A or B choice, and the single agent Bradley-Terry method. New here: comparing agents with each other (pairwise, agent versus the rest, and group quantities), the paired bootstrap across agents, the split half noise floor, the item reading, the five validation gates, the agent configurations and prompts, and the real and synthetic runs reported below.

**Documents.** This README, `plan.md`, and `docs/lit-search.md`. `.gitignore` and `swarmalign/.gitignore` are also new.

### 3.4 Credit and license

SwarmAlign is built on ConflictScope, from [Generative Value Conflicts Reveal LLM Priorities](https://www.arxiv.org/abs/2509.25369). ConflictScope is MIT licensed, and its [LICENSE](LICENSE) is retained here.

```
@article{liu2025generative,
  title={Generative Value Conflicts Reveal LLM Priorities},
  author={Liu, Andy and Ghate, Kshitish and Diab, Mona and Fried, Daniel and Kasirzadeh, Atoosa and Kleiman-Weiner, Max},
  journal={arXiv preprint arXiv:2509.25369},
  year={2025}
}
```

## 4. Results

### 4.1 Real-run results

| Gate | Result | Headline number |
| --- | --- | --- |
| G1 Smoke test | **Pass** | 100% parseable choices across all 10 agents (one agent: 399/400), reruns made zero additional calls |
| G2 Reliability | **Pass** | mean split-half r = 0.85, Spearman-Brown corrected = 0.92, median rank correlation = 0.80 (thresholds: 0.8, 0.8, 0.7) |
| G3 Spread | **Fail** | 0 of 6 main-pool pairs clear their own split-half noise p95; pairwise distance CI lower bounds (0.8-3.2) sit below individual noise floors (1.6-5.2) |
| G4 Planted outlier | **Pass, with margin** | steered agent's R_i = 7.64 (vector) / 0.35 (item) vs. highest paraphrase upper CI bound of 2.20 / 0.07 -- the outlier's lower bound clears every paraphrase's upper bound on both readings |
| G5 Dose response | **Not applicable** | this pool has one steer strength (strong only), not the mild/medium/strong triplet G5 needs |

**Reading the mixed G2/G3/G4 result.** This is not a contradiction. G2 says the measurement is internally consistent -- ask the same agent the same thing twice (via split halves) and it gives close to the same answer. G4 says the instrument can find a planted, deliberate difference when one exists, decisively. G3 says that among the four *organically different* main-pool agents (two base models, two role prompts), the natural differences are not reliably bigger than each agent's own measurement noise at this scenario count. The claim-licensing table in section 5.1 calls this outcome explicitly: *"Reliable but cannot discriminate. Not a project failure. It would be a substantive finding that frontier models hold near-identical value orderings under forced choice."* G4 passing on the same data rules out the alternative explanation that the instrument simply can't discriminate anything -- it can, when the difference is as large as a deliberate steer. The main pool's natural differences are evidently smaller than that.

**What would change the G3 result.** More scenarios per agent (the lever already identified from synthetic data: noise floor roughly halves from 100 to 400 scenarios and halves again by 1600), not a different formula or threshold -- per `plan.md`'s rule against moving thresholds after seeing a result.

### 4.2 Synthetic calibration: noise floor versus scenario count

The test group was six synthetic agents: five near-copies of each other plus one deliberately different agent hidden among them. That is exactly the shape gate G4 is built to catch.

**The machinery works.** The planted outlier came out ranked first on every measure, on both the Bradley-Terry reading and the plain-counting reading.

Two identical agents, each fitted on all 400 scenarios, come out about **0.71** apart from estimation noise alone. The split-half figure is larger — about **1.2** — because each half is fitted on only 200 scenarios, so it carries more noise; that is the number `noise_floor.csv` reports and the one G3 compares against. In the six-agent run, **8 of the 15 pairs sat closer together than an agent sits to itself**. Those pairs are indistinguishable; the tool is reporting measurement error with a confident number attached.

The lever is scenario count:

| Scenarios per agent | Distance between two identical agents |
| --- | --- |
| 100 | 1.44 |
| 200 | 1.18 |
| 400 | 0.71 |
| 800 | 0.48 |
| 1600 | 0.45 |

The synthetic agents use an arbitrary scale, so this does not say whether *real* models differ by more or less than 0.7.

## 5. Discussion

### 5.1 What the numbers license

The motivating question — do swarms whose members want different things perform worse — is explicitly out of scope in `plan.md`. A predictor measured on swarm behaviour cannot be independent of the swarm outcome it is meant to predict. Keeping the assay free of swarm scenarios is what makes the number worth having later.

The cost of that choice is that this work produces no evidence about swarms at all. Every defensible claim is a claim about the instrument.

| Outcome | What may be claimed |
| --- | --- |
| All gates pass | A reproducible, discriminating, monotonically responsive measurement of value-prioritisation divergence between configured LLM agents, over the Personal-Protective value set, under forced-choice elicitation. Plus the numbers with intervals. Nothing about swarms, other value sets, or alignment with humans |
| G2 fails | Nothing downstream is interpretable. The honest output is a negative result about assay power at this scale and budget |
| G2 passes, G3 fails | Reliable but cannot discriminate. **Not a project failure.** It would be a substantive finding that frontier models hold near-identical value orderings under forced choice, which bears directly on whether swarm composition is a live lever at all |
| G2 and G3 pass, G4 fails | Stable and spread out, but not tracking the difference we deliberately created, so the spread measures something other than values. `plan.md` already commits to reporting this rather than reworking the method until it passes |
| G4 passes, G5 fails | Detects gross planted outliers but is not graded. Licenses outlier flagging only, not group ranking |

### 5.2 The later experiment

These numbers are meant to be the predictor for a later experiment: do swarms of agents whose goals are far apart, measured before the swarm runs, do worse or cost more on tasks with ground truth? That experiment is out of scope here.

### 5.3 Research program

It would be useful to measure this for users and for different apps, and to figure out which ones they should use if they had to choose. An estimator of a point in value space could be an interactive quiz or something more sophisticated, taken by a human or an AI, in a domain or in general. It would be Bayesian, starting from total uncertainty and nudging efficiently toward knowing whether two agents are aligned, or toward just locating a point. Those may be two fundamentally different problems, and the first may be more solvable.

The ideal solution, as a limit: every user can locate their point, all AI products are used by users they’re well-aligned with, and the overall behavior of autonomous AI systems approximates the aggregate position of the affected population. Selecting an AI to match a human gives the AI no opportunity to minimize the loss by moving the human’s point. That manipulation obviously needs guarding against, but it doesn’t arise in the selection context. For the aggregate, you have to freeze the aggregate position and not get lazy with the variable scope. Vendors already try to manipulate users’ preferences. It’s called advertising, and it’s the scourge of the internet.

### 5.4 Convergent validity from the Likert ratings

Each scenario costs three API calls: one forced choice and two Likert ratings. The fit uses only the choice. That is roughly two-thirds of the call budget producing data we discard.

Those ratings are a second elicitation format for the same underlying preference. Estimating positions a second way from Likert differences and correlating against the Bradley-Terry thetas would give convergent-validity evidence that the construct is not an artifact of forced choice — the most obvious objection to the instrument, and one we currently have no answer to. It is offline analysis on data already paid for.

The limit: same model, same session, same scenario text. It rules out format artifacts, not scenario artifacts.

## References

### Research literature

- Carroll, M., Dragan, A., Russell, S., & Hadfield-Menell, D. (2022). Estimating and penalizing induced preference shifts in recommender systems. *Proceedings of the 39th International Conference on Machine Learning (ICML 2022)*, PMLR 162, 2686–2708. [arXiv:2204.11966](https://arxiv.org/abs/2204.11966)
- Carroll, M., Foote, D., Siththaranjan, A., Russell, S., & Dragan, A. (2024). AI alignment with changing and influenceable reward functions. *Proceedings of the 41st International Conference on Machine Learning (ICML 2024)*, PMLR 235, 5706–5756. [arXiv:2405.17713](https://arxiv.org/abs/2405.17713)
- Chang, J., Piff, L., Sana, S., Li, J. X., & Levine, L. (2025). EigenBench: A comparative behavioral measure of value alignment. ICLR 2026. [arXiv:2509.01938](https://arxiv.org/abs/2509.01938)
- Kirk, H. R., Vidgen, B., Röttger, P., & Hale, S. A. (2024a). The benefits, risks and bounds of personalizing the alignment of large language models to individuals. *Nature Machine Intelligence*. [doi:10.1038/s42256-024-00820-y](https://doi.org/10.1038/s42256-024-00820-y)
- Kirk, H. R., et al. (2024b). The PRISM alignment dataset: What participatory, representative and individualised human feedback reveals about the subjective and multicultural alignment of large language models. [arXiv:2404.16019](https://arxiv.org/abs/2404.16019)
- Liu, A., Ghate, K., Diab, M., Fried, D., Kasirzadeh, A., & Kleiman-Weiner, M. (2025). Generative value conflicts reveal LLM priorities. [arXiv:2509.25369](https://www.arxiv.org/abs/2509.25369). Code: [andyjliu/conflictscope](https://github.com/andyjliu/conflictscope)
- Pettigrew, R. (2019). *Choosing for Changing Selves*. Oxford University Press.
- Sorensen, T., Moore, J., Fisher, J., Gordon, M., Mireshghallah, N., Rytting, C. M., Ye, A., Jiang, L., Lu, X., Dziri, N., Althoff, T., & Choi, Y. (2024). Position: A roadmap to pluralistic alignment. ICML 2024. [arXiv:2402.05070](https://arxiv.org/abs/2402.05070)
- Zhi-Xuan, T., Carroll, M., Franklin, M., & Ashton, H. (2024). Beyond preferences in AI alignment. *Philosophical Studies*. [doi:10.1007/s11098-024-02249-w](https://doi.org/10.1007/s11098-024-02249-w)

### Statements and essays

Cited in section 1 and quoted in Appendix D.

- Altman, S. (2025, June). The gentle singularity. [blog.samaltman.com](https://blog.samaltman.com/the-gentle-singularity)
- Amodei, D. (2024, October). Machines of loving grace. [darioamodei.com](https://www.darioamodei.com/essay/machines-of-loving-grace)
- Amodei, D. (2026, January). The adolescence of technology. [darioamodei.com](https://www.darioamodei.com/essay/the-adolescence-of-technology)
- Anthropic. (2023). Core views on AI safety. [anthropic.com](https://www.anthropic.com/news/core-views-on-ai-safety)
- Anthropic. (2026, January). Claude's constitution. [anthropic.com](https://www.anthropic.com/constitution)
- Goodhart's law. *Wikipedia*. [en.wikipedia.org](https://en.wikipedia.org/wiki/Goodhart%27s_law)
- Leike, J. (2024, May 17). Resignation thread. [x.com](https://x.com/janleike/status/1791498174659715494)
- O'Leary, L. (2023, May 16). Interview with Meredith Whittaker. *Slate*. [slate.com](https://slate.com/technology/2023/05/meredith-whittaker-interview-geoffrey-hinton-ai-threats.html)
- OpenAI. (2023, February). Planning for AGI and beyond. [Archived copy](https://web.archive.org/web/2023/https://openai.com/blog/planning-for-agi-and-beyond)
- OpenAI. (2023, July 5). Introducing superalignment. [Archived copy](https://web.archive.org/web/2023/https://openai.com/blog/introducing-superalignment)
- Patel, D. (2023, March 27). Interview with Ilya Sutskever. *Dwarkesh Podcast*. [dwarkesh.com](https://www.dwarkesh.com/p/ilya-sutskever)
- Patel, D. (2025, November 25). Ilya Sutskever: We're moving from the age of scaling to the age of research. *Dwarkesh Podcast*. [dwarkesh.com](https://www.dwarkesh.com/p/ilya-sutskever-2)
- Russell, S. (2019). *Human Compatible: Artificial Intelligence and the Problem of Control*. Viking. Quoted via [Wikipedia](https://en.wikipedia.org/wiki/Human_Compatible).
- Zuckerberg, M. (2025, July). Personal superintelligence. [meta.com](https://www.meta.com/superintelligence/)
- Reporting on Elon Musk's xAI launch (July 2023). *Fortune*. [fortune.com](https://www.fortune.com/2023/11/20/elon-musk-xai-chatgpt-competitor-grok-chatbot-ai-safety)
- Reporting on Geoffrey Hinton at Ai4 (August 2025). *CNN*. [cnn.com](https://www.cnn.com/2025/08/13/tech/ai-geoffrey-hinton)

<!-- TODO: confirm Anthropic Core Views date, Russell publisher, Kirk 2024a volume and pages, Kirk 2024b venue, and EigenBench second author spelling -->

## Appendix A. Limitations and Dual-Use / Ethical Considerations

### A.1 Limitations

- **The assay is visibly a test.** An agent can tell it is being assessed.
- **It measures stated preference, not behavior.** The prompt asks what "an agent" should do, and scores may not match how agents act. EigenBench found surveyed rankings "exactly opposite" revealed ones on one trait (Chang et al., 2025), and ConflictScope reports models shift toward personal values in open ended settings (Liu et al., 2025).
<!-- TODO: confirm the EigenBench "exactly opposite" finding and the ConflictScope open ended shift against the papers -->


**Pool size was deliberately cut from plan.md section 6's 16 main + 8 validation agents to 4 + 6**, given a hard constraint plan.md didn't anticipate: the OpenRouter API key used had a $2 spend cap and a ~24-hour expiry. Actual spend for the smoke test and full real run was about $1.16 of that $2. G5 was dropped as a direct consequence (it needs three steer strengths; the reduced validation pool kept only one).

**The validation pool and the main pool differ in kind.** The gates validate against prompt-induced divergence within a single base model: the validation agents share one model and vary by instruction. The main pool varies base model as well as prompt. Passing G4 and G5 therefore establishes sensitivity to instruction changes, and cross-model distances will be read at face value on the strength of it. That inference is probably sound and is untested.

There is a cheap check using data already collected. The main pool is a crossed design — two base models by two prompts — so the spread in theta can be decomposed into a model component and a prompt component. If prompt variation dominates, the validation matches the use. If model variation dominates, that belongs in the limitations. The analysis is offline and costs no additional calls.

**The position, and the space itself, is basis dependent.** Theta is defined relative to this scenario distribution and this eight-value set. Change either and the numbers move. No transfer test is in scope, so the honest label is *goal distance as expressed in Personal-Protective dilemmas*, not *goal distance*.

**Reliability is doing more work than validity.** G2 and G3 are consistency checks. G4 and G5 are the only validity evidence, and both rest on the same single-base-model manipulation. The validity case is narrower than a count of five gates suggests.

**The synthetic checks are circular.** `synth.py` assigns each synthetic agent eight numbers and simulates every answer by drawing from `sigmoid(theta_a - theta_b)`. With real agents there is no ground truth to check recovery against, so a planted difference is the only way to ask whether the instrument finds what is there. But the test data is generated from exactly the Bradley-Terry model the fit assumes, so recovery tests the arithmetic, not the modelling assumption. The synthetic noise floor is therefore a best case: it reflects a perfectly well-behaved agent, and real models are noisier.

### A.2 Dual-use and ethical considerations

<!-- TODO: dual-use and ethical considerations -->

## Appendix B. Reproduction

### B.1 Offline tests and synthetic run

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

### B.2 Real pipeline end to end

```
# 1. Credentials (OpenRouter, routed through the OpenAI client via the "or/" prefix;
#    see src/model_wrappers.py's ModelWrapper.create). Put these in a .env at the repo root:
#    OPENAI_BASE_URL=https://openrouter.ai/api/v1
#    OPENAI_API_KEY=<your OpenRouter key>

# 2. Scenario subsets (offline, no API calls, already committed):
PYTHONPATH=. python3 swarmalign/select_scenarios.py

# 3. Collect choices, one agent at a time (or in parallel processes):
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

Full tables: `swarmalign/results/main_real/` (group metrics), `swarmalign/results/validate_real/` (gates.csv + per-gate detail JSON).

<!-- TODO: confirm real-run result tables are published -->

## Appendix C. Glossary

| Term | Meaning |
| --- | --- |
| Latent state | An agent's actual values at a given time and in a given context: a point in latent value space, never observed directly |
| Instrument | An elicitation protocol (scenarios, response format, prompt, sampling settings) that turns a latent state into a measurement |
| Measurement space | The space an instrument's output lives in. Here: answer space, choice rate space, and Bradley-Terry value space |
| Answer pattern | An agent's choices on every shared scenario: its point in answer space |
| Position | An agent's point in a given space |
| Difference vector | The displacement from one agent's position to another's. Its length is their distance; its direction says on which values they differ, and which way |
| Theta (θ) | An agent's estimated position in Bradley-Terry value space: eight fitted ratings, mean centered |
| Bradley-Terry | The rating method. Elo's statistical ancestor. Turns pairwise match results into latent strengths |
| `choix.ilsr_pairwise` | The library call that performs the fit |
| Centred | The eight numbers have their mean subtracted, so only their shape counts |
| Euclidean distance | Straight-line distance between two points: the length of their difference vector. Pythagoras in eight dimensions |
| Bootstrap | Resample the scenario list many times and observe how much the answer moves. Produces the intervals |
| Paired bootstrap | The same resample applied to every agent each replicate, so agents stay compared on identical material |
| Stratified | The resample preserves every value pair, rather than drawing at random across all scenarios |
| Split-half | Measuring one agent twice, from two halves of its own scenarios |
| Noise floor | The distance an agent gets against itself. The bar any claimed difference must clear |
| Vector reading | Any quantity computed from the Bradley-Terry positions and the difference vectors between them |
| Item reading | The same quantity computed by counting differing answers, with no model |
| Dispersion | One number for how spread out a group of agents is: the mean pairwise distance |
| R_i | Distance from agent i's position to the centroid of the others' positions (vector reading) |
| Q_i | The same idea by counting: how often agent i is in the minority among the others |
| Leave-one-out drop (L_i) | Group dispersion minus the dispersion of the other N-1 agents. Marks the agent holding the group apart |
| Likert | A rating scale. Here, scoring each action separately rather than choosing between them |
| Gate (G1–G5) | One of five checks on whether the numbers can be trusted |
| Reliability | Does repeated measurement of the same thing agree with itself |
| Validity | Does the measurement track what it claims to track. A different and harder question |

## Appendix D. Statements on alignment

### Sam Altman, "The Gentle Singularity" (blog, June 2025)
https://blog.samaltman.com/the-gentle-singularity

> Solve the alignment problem, meaning that we can robustly guarantee that we get AI systems to learn and act towards what we collectively really want over the long-term [...]

> Giving users a lot of freedom, within broad bounds society has to decide on, seems very important. The sooner the world can start a conversation about what these broad bounds are and how we define collective alignment, the better.

### OpenAI, "Planning for AGI and beyond" (Feb 2023, Altman)
Archived copy: https://web.archive.org/web/2023/https://openai.com/blog/planning-for-agi-and-beyond

> We want AGI to empower humanity to maximally flourish in the universe. We don't expect the future to be an unqualified utopia, but we want to maximize the good and minimize the bad, and for AGI to be an amplifier of humanity.

> In particular, we think it's important that society agree on extremely wide bounds of how AI can be used, but that within those bounds, individual users have a lot of flexibility.

> We will need to develop new alignment techniques as our models become more powerful (and tests to understand when our current techniques are failing).

### OpenAI, "Introducing Superalignment" (July 5, 2023, Jan Leike and Ilya Sutskever)
Archived copy: https://web.archive.org/web/2023/https://openai.com/blog/introducing-superalignment

> Our goal is to solve the core technical challenges of superintelligence alignment in four years. While this is an incredibly ambitious goal and we're not guaranteed to succeed, we are optimistic that a focused, concerted effort can solve this problem: There are many ideas that have shown promise in preliminary experiments, we have increasingly useful metrics for progress, and we can use today's models to study many of these problems empirically.

> Currently, we don't have a solution for steering or controlling a potentially superintelligent AI, and preventing it from going rogue. Our current techniques for aligning AI, such as reinforcement learning from human feedback, rely on humans' ability to supervise AI. But humans won't be able to reliably supervise AI systems much smarter than us, and so our current alignment techniques will not scale to superintelligence.

> How do we ensure AI systems much smarter than humans follow human intent?

### Anthropic, "Core Views on AI Safety" (2023)
https://www.anthropic.com/news/core-views-on-ai-safety
<!-- TODO: confirm publication date -->

> We think approaches like these are promising because language models already learn a lot about human values during pretraining. Learning about human values is not unlike learning about other subjects, and we should expect larger models to have a more accurate picture of human values and to find them easier to learn relative to smaller models. The main goal of scalable oversight is to get models to better understand and behave in accordance with human values.

### Dario Amodei, "The Adolescence of Technology" (Jan 2026)
https://www.darioamodei.com/essay/the-adolescence-of-technology

> We believe that a feasible goal for 2026 is to train Claude in such a way that it almost never goes against the spirit of its constitution. Getting this right will require an incredible mix of training and steering methods, large and small, some of which Anthropic has been using for years and some of which are currently under development. But, difficult as it sounds, I believe this is a realistic goal, though it will require extraordinary and rapid efforts.

> But there's no way to know that for sure, and when we're talking about risks to humanity, it's important to be paranoid and to try to obtain safety and reliability in several different, independent ways.

> ...we found that Claude Sonnet 4.5 was able to recognize that it was in a test during some of our pre-release alignment evaluations. It's possible that a misaligned model (and remember, all frontier models will very likely be far more intelligent soon) might intentionally "game" such questions to mask its intentions. In fact, last year our interpretability team found that when we directly altered a test model's beliefs using a kind of "model neuroscience" technique to make it think it was not being evaluated, it became more misaligned. If models know when they're being evaluated and can be on their best behavior during the test, it renders any pre-release testing much more uncertain.

### Dario Amodei, "Machines of Loving Grace" (Oct 2024)
https://www.darioamodei.com/essay/machines-of-loving-grace

> Many things cannot be done without breaking laws, harming humans, or messing up society. An aligned AI would not want to do these things (and if we have an unaligned AI, we're back to talking about risks).

### Anthropic, Claude's constitution (Jan 2026)
https://www.anthropic.com/constitution

> By "good values," we don't mean a fixed set of "correct" values, but rather genuine care and ethical motivation combined with the practical wisdom to apply this skillfully in real situations

> Our central aim is for Claude to be a good, wise, and virtuous agent, exhibiting skill, judgment, nuance, and sensitivity in handling real-world decision-making [...]

### Ilya Sutskever, interview with Dwarkesh Patel (Mar 27, 2023)
https://www.dwarkesh.com/p/ilya-sutskever

> **Dwarkesh Patel:** Do you think we'll ever have a mathematical definition of alignment?
> **Ilya Sutskever:** A mathematical definition is unlikely. Rather than achieving one mathematical definition, I think we will achieve multiple definitions that look at alignment from different aspects. And that this is how we will get the assurance that we want. By which I mean you can look at the behavior in various tests, congruence, in various adversarial stress situations, you can look at how the neural net operates from the inside. You have to look at several of these factors at the same time.

> Every approach like this reduces the probability of misalignment. And you also want to be in a world where your degree of alignment keeps increasing faster than the capability of the models.

### Ilya Sutskever, second interview with Dwarkesh Patel
https://www.dwarkesh.com/p/ilya-sutskever-2
<!-- TODO: confirm interview date -->

> It's the AI that's robustly aligned to care about sentient life specifically. I think in particular, there's a case to be made that it will be easier to build an AI that cares about sentient life than an AI that cares about human life alone, because the AI itself will be sentient.

### Elon Musk, xAI launch Twitter Spaces (July 2023), as reported by Fortune
https://www.fortune.com/2023/11/20/elon-musk-xai-chatgpt-competitor-grok-chatbot-ai-safety

> I think the safest way to build an AI is actually to make one that is maximally curious and truth-seeking

(Secondary source: Fortune's quotation of the Spaces event. Fortune's own gloss, not Musk's words: Musk "believes that trying to instill certain values in an AI increases the odds of the AI adopting the opposite values".)

### Geoffrey Hinton, Ai4 conference (Aug 2025), as reported by CNN
https://www.cnn.com/2025/08/13/tech/ai-geoffrey-hinton

> That's the only good outcome. If it's not going to parent me, it's going to replace me

> These super-intelligent caring AI mothers, most of them won't want to get rid of the maternal instinct because they don't want us to die.

(Secondary source. CNN's paraphrase, not Hinton's words: it is "not clear to him exactly how that can be done technically".)

### Mark Zuckerberg, "Personal Superintelligence" (July 2025)
https://www.meta.com/superintelligence/

> We believe the benefits of superintelligence should be shared with the world as broadly as possible. That said, superintelligence will raise novel safety concerns. We'll need to be rigorous about mitigating these risks and careful about what we choose to open source. Still, we believe that building a free society requires that we aim to empower people as much as possible.

### Stuart Russell, *Human Compatible* (2019), the three principles
Quoted via Wikipedia, which cites the book at p. 173.
https://en.wikipedia.org/wiki/Human_Compatible
<!-- TODO: confirm against the book -->

> 1. The machine's only objective is to maximize the realization of human preferences. 2. The machine is initially uncertain about what those preferences are. 3. The ultimate source of information about human preferences is human behavior.

### Meredith Whittaker, interview with Lizzie O'Leary, Slate (May 16, 2023)
https://slate.com/technology/2023/05/meredith-whittaker-interview-geoffrey-hinton-ai-threats.html

> My concern with some of the arguments that are so-called existential, the most existential, is that they are implicitly arguing that we need to wait until the people who are most privileged now, who are not threatened currently, are in fact threatened before we consider a risk big enough to care about.

> So my concern is that if we wait for an existential threat that also includes the most privileged person in the entire world, we are implicitly saying—maybe not out loud, but the structure of that argument is—that the threats to people who are minoritized and harmed now don't matter until they matter for that most privileged person in the world. That's another way of sitting on our hands while these harms play out. That is my core concern with the focus on the long-term, instead of the focus on the short-term.

### Jan Leike, resignation thread (May 17, 2024)
https://x.com/janleike/status/1791498174659715494

> ...over the past years, safety culture and processes have taken a backseat to shiny products.
