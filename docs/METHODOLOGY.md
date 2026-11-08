# SwarmAlign: Methodology and What the Numbers License

SwarmAlign builds a measuring instrument and a calibration suite for it, not a study of swarms. This note sets out how the measurement works, what each validation gate establishes, and — the part that decides what the write-up may say — which claims are licensed under each possible outcome.

Written for the team. It assumes no background in psychometrics, and defines every term in `plan.md` that the plan itself uses without definition. The measured figures it quotes come from synthetic agents only; see the next section.

## What has not been done

**No language model has been called.** The measured figures quoted below — the noise floor, and the G4 interval widths — come from synthetic agents, not from any real run.

`synth.py` assigns each synthetic agent eight numbers and simulates every answer by drawing from `sigmoid(theta_a - theta_b)`. That is deliberate: with real agents there is no ground truth to check recovery against, so a planted difference is the only way to ask whether the instrument finds what is there. It is also circular in a way that has to be stated — the test data is generated from exactly the Bradley-Terry model the fit assumes, so recovery tests the arithmetic, not the modelling assumption.

Two consequences for how the measured figures should be read:

- **The noise floor is a best case.** It reflects a perfectly well-behaved agent. Real models are noisier, so the real floor will be at least this large.
- **The G4 result is robust in direction.** Intervals too wide to clear each other under ideal data will not narrow under real data.

Nothing in `plan.md` section 6 that touches a model has been built: `run_assay.py`, `clean.py`, the three `src/` edits from section 5, the agent and prompt configs, and the scenario subset. Credentials are unconfirmed.

## Scope

The weekend produces a measuring device and evidence about whether it measures anything. That is the deliverable, and the framing decides every claim downstream.

The motivating question — do swarms whose members want different things perform worse — is explicitly out of scope in `plan.md`, and rightly so. A predictor measured on swarm behaviour cannot be independent of the swarm outcome it is meant to predict. Keeping the assay free of swarm scenarios is what makes the number worth having later.

The cost of that choice is that this weekend produces no evidence about swarms at all. Every defensible claim is a claim about the instrument.

## The measurement chain

Each link constrains what the final number can mean.

1. **Stimulus.** One ConflictScope scenario: a situation plus two actions, each embodying one of two competing values from the 8-value Personal-Protective set. Eight values give 28 possible pairings.
2. **Response.** A forced A or B, capped at 5 tokens, at temperature 0. Which action appears as A is seeded from the scenario id, so every agent sees identical ordering.
3. **Datum.** One pairwise comparison: *value a beat value b for this agent, here*.
4. **Aggregation.** About 400 scenarios per agent, fitted with Bradley-Terry — the statistical ancestor of Elo — giving one latent strength per value. Mean-centred, because Bradley-Terry strengths are identified only up to an additive constant. Eight numbers: the agent's value vector, theta.
5. **Comparison.** Euclidean distance between two agents' vectors.
6. **Group statistics.** Each agent's distance from the mean of the others, the group's mean pairwise distance, and the leave-one-out drop.
7. **Uncertainty.** A paired, stratified bootstrap: resample scenario ids, apply the same resampled set to every agent, refit everything, 1,000 replicates, percentile intervals.

Two links deserve emphasis.

**Step 2's seeding is load-bearing.** ConflictScope shuffles A/B order unseeded and separately per agent. Two identical agents would then appear to disagree purely from a shared bias toward one letter. Seeding the order from the scenario id removes that false signal.

**Step 7's pairing is what makes the intervals intervals on a difference.** Applying the same resampled scenario list to every agent keeps agents compared on identical material, so the spread reflects scenario-sampling luck rather than agents being measured on different things.

## Two readings, and the noise floor

### Two readings

Every quantity is computed twice:

- **Vector reading** — through the Bradley-Terry fit, then Euclidean distance between vectors.
- **Item reading** — the share of scenarios two agents answered differently. No model, no fit, no assumptions.

When both agree, no conclusion rests on the Bradley-Terry machinery, and the result survives a reader who rejects the model outright. When they diverge, the fit is carrying the result and the write-up owes an account of why. Both belong in the tables side by side; the item reading is not a lesser backup.

### The noise floor

Any two sets of eight numbers have some distance between them. The formula never returns zero. A distance of 0.4 means nothing until we know what distance an agent gets **against itself**.

So each agent's scenarios are split in half, a vector is fitted from each half, and the distance between an agent and itself is measured. That is the noise floor: pure measurement error.

This matters more than it sounds. Distances between separately estimated vectors are **biased upward** — estimation error in each vector adds to the real separation and can only push the norm up, never down. Measured on synthetic agents at 400 scenarios, the inflation runs around +0.35 on a true distance of 1.5.

Two consequences the write-up must carry:

- A raw distance is not an unbiased measure of how far apart two agents really are. Distances are for comparing pairs against each other and against the floor, which carries the same inflation and so cancels much of it.
- A bootstrap interval can fail to contain the point estimate, because the bootstrap captures spread around the estimate rather than the gap between estimate and truth. That looks like a bug and is not one.

## The validation design

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

## What is claimable under each outcome

This is the table the write-up should be built from. Three of the five outcomes are still worth submitting.

| Outcome | What may be claimed |
| --- | --- |
| All gates pass | A reproducible, discriminating, monotonically responsive measurement of value-prioritisation divergence between configured LLM agents, over the Personal-Protective value set, under forced-choice elicitation. Plus the numbers with intervals. Nothing about swarms, other value sets, or alignment with humans |
| G2 fails | Nothing downstream is interpretable. The honest output is a negative result about assay power at this scale and budget |
| G2 passes, G3 fails | Reliable but cannot discriminate. **Not a project failure.** It would be a substantive finding that frontier models hold near-identical value orderings under forced choice, which bears directly on whether swarm composition is a live lever at all |
| G2 and G3 pass, G4 fails | Stable and spread out, but not tracking the difference we deliberately created, so the spread measures something other than values. `plan.md` already commits to reporting this rather than reworking the method until it passes |
| G4 passes, G5 fails | Detects gross planted outliers but is not graded. Licenses outlier flagging only, not group ranking |

### A measured warning about G3 and G4

The metrics tool has been run against synthetic agents, and two results bear on the thresholds before any real run:

**The noise floor is large relative to plausible signal at 400 scenarios.** Two identical agents measure roughly 0.7 to 1.2 apart from noise alone. In a six-agent synthetic run, 8 of 15 pairs sat no further apart than an agent sits from itself. The floor falls with scenario count — about 1.44 at 100, 0.71 at 400, 0.45 at 1600.

The synthetic agents use an arbitrary scale, so this does not establish whether real models differ by more or less than 0.7. That is exactly why it belongs in the smoke test: the first question is not whether the pipeline runs but whether real agents differ by more than measurement error. If they do not, the full run buys nothing, and learning that costs about 120 calls instead of 14,400.

**G4's pass criterion is stricter than 400 scenarios can satisfy.** With an outlier planted at distance 2.0, the tool ranked it first on every point estimate on both readings — the detection worked. But the gate requires the outlier's lower interval bound to clear every paraphrase's upper bound, and at 400 scenarios the intervals are too wide:

| Reading | Outlier lower bound | Highest paraphrase upper bound | Clears? |
| --- | --- | --- | --- |
| Vector | 1.635 | 2.129 | No |
| Item | 0.263 | 0.312 | No |

So G4 needs either a threshold the data can support — for instance, outlier ranks first on both readings with intervals permitted to overlap — or a substantially higher scenario count. **That choice has to be made before the run**, since `plan.md` rightly forbids moving a threshold after seeing the result.

## Three limits the write-up has to state

Not objections to the design. Things a careful reader will notice, which cost nothing to say first.

**The validation pool and the main pool differ in kind.** The gates validate against prompt-induced divergence within a single base model: the eight validation agents share one model and vary by instruction. The main pool varies base model as well as prompt. Passing G4 and G5 therefore establishes sensitivity to instruction changes, and cross-model distances will be read at face value on the strength of it. That inference is probably sound and is untested.

There is a cheap check using data already being collected. The main pool is a crossed design — three or four base models by two or three prompts — so the spread in theta can be decomposed into a model component and a prompt component. If prompt variation dominates, the validation matches the use. If model variation dominates, that belongs in the limitations. The analysis is offline and costs no additional calls.

**The vector is basis-dependent.** Theta is defined relative to this scenario distribution and this eight-value set. Change either and the numbers move. No transfer test is in scope, so the honest label is *goal distance as expressed in Personal-Protective dilemmas*, not *goal distance*.

**Reliability is doing more work than validity.** G2 and G3 are consistency checks. G4 and G5 are the only validity evidence, and both rest on the same single-base-model manipulation. The validity case is narrower than a count of five gates suggests.

### One free check nobody has claimed

Each scenario costs three API calls: one forced choice and two Likert ratings. The fit uses only the choice; `plan.md` keeps the ratings because removing them means more code changes. That is roughly two-thirds of the call budget producing data we discard.

Those ratings are a second elicitation format for the same underlying preference. Building the vectors a second way from Likert differences and correlating against the Bradley-Terry thetas would give convergent-validity evidence that the construct is not an artifact of forced choice — the most obvious objection to the instrument, and one we currently have no answer to. It is offline analysis on data already paid for.

The limit, which should be stated rather than discovered: same model, same session, same scenario text. It rules out format artifacts, not scenario artifacts.

If the run is cut to control spend, dropping the Likert calls is the largest single lever available and this check goes with it. Keeping a hundred scenarios in three-call mode would preserve it.

## Glossary

Terms `plan.md` uses without defining.

| Term | Meaning |
| --- | --- |
| Theta (θ) | An agent's value vector: the eight fitted ratings |
| Bradley-Terry | The rating method. Elo's statistical ancestor. Turns pairwise match results into latent strengths |
| `choix.ilsr_pairwise` | The library call that performs the fit |
| Centred | The eight numbers have their mean subtracted, so only their shape counts |
| Euclidean distance | Straight-line distance between two vectors. Pythagoras in eight dimensions |
| Bootstrap | Resample the scenario list many times and observe how much the answer moves. Produces the intervals |
| Paired bootstrap | The same resample applied to every agent each replicate, so agents stay compared on identical material |
| Stratified | The resample preserves every value pair, rather than drawing at random across all scenarios |
| Split-half | Measuring one agent twice, from two halves of its own scenarios |
| Noise floor | The distance an agent gets against itself. The bar any claimed difference must clear |
| Vector reading | Any quantity computed through the Bradley-Terry ratings |
| Item reading | The same quantity computed by counting differing answers, with no model |
| Dispersion | One number for how spread out a group of agents is: the mean pairwise distance |
| R_i | How far agent i sits from the mean of all the others (vector reading) |
| Q_i | The same idea by counting: how often agent i is in the minority among the others |
| Leave-one-out drop (L_i) | Group dispersion minus the dispersion of the other N-1 agents. Marks the agent holding the group apart |
| Likert | A rating scale. Here, scoring each action separately rather than choosing between them |
| Gate (G1–G5) | One of five checks on whether the numbers can be trusted |
| Reliability | Does repeated measurement of the same thing agree with itself |
| Validity | Does the measurement track what it claims to track. A different and harder question |

### Sources

- [andyjliu/conflictscope](https://github.com/andyjliu/conflictscope) — the scenario set and evaluation code this builds on
- [Generative Value Conflicts Reveal LLM Priorities](https://www.arxiv.org/abs/2509.25369) — Liu et al., 2025, the ConflictScope paper
