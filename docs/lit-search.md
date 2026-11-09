# Literature search: value distance between agents

Searched Nov 6, 2026.

## Question

Has anyone measured value distance between agents before they interact, then used it to predict multi-agent task performance?

## Finding

No such paper was found. This was a limited search: seven web queries and three papers read closely, plus [A Roadmap to Pluralistic Alignment](https://arxiv.org/abs/2402.05070). It supports "we did not find it," not "nobody has done it."

Safe wording: "We did not find prior work that uses pre-interaction value distance between agents to predict multi-agent task performance." The hackathon build produces the predictor, not the prediction, so any claim should stay about the direction of the work.

## Papers read closely

| Paper | How values are obtained | Distance between agent pairs | Measured first, then used to predict | Outcome |
| --- | --- | --- | --- | --- |
| [CIVA](https://arxiv.org/abs/2604.05339) | Assigned by prompt | None found | No, prevalence is a control setting | Community collapse, cooperation |
| [ValueFlow](https://arxiv.org/html/2602.08567) | Questions scored by an LLM judge | None found | Partly: per agent susceptibility predicts value spread, weakly on held out data (ρ = 0.54, p = 0.27, from a summarized appendix) | Value drift, not task performance |
| [EigenBench](https://arxiv.org/html/2509.01938v2) | Models judge each other's answers | None, ranks models against a constitution | No | Its own score, with no ground truth |

Appendices of CIVA and ValueFlow were read only in summary form.

## Closest neighbor, not read

A [Nature Scientific Reports paper](https://www.nature.com/articles/s41598-025-25531-1) reportedly groups agent pairs by value similarity and compares their mutual trust. The page would not load, so only a search summary is available, and that summary gave an inconsistent article number. As described, values are assigned and the outcome is trust, not task performance. Read this paper before making any novelty claim.

## Implications for SwarmAlign

- **Validation has precedent.** EigenBench added 0 to 5 planted "greenbeard" personas and watched their scores rise, which is close to gates G4 and G5. It also fits Bradley-Terry style preferences.
- **Multiple choice may not match behavior.** EigenBench found surveyed rankings on conservatism were "exactly opposite" the rankings revealed by behavior. The [ConflictScope paper](https://arxiv.org/abs/2509.25369v1) reports models shift toward personal values in open ended settings.
- **Steering should work to some degree.** The ConflictScope paper reports that value orderings in system prompts improved alignment with a target ranking by 14%, according to a search summary. This may not hold for cheap models.
- **Distance may not always hurt.** Diversity results are mixed. [LLM team diversity often reduced accuracy on reasoning tasks](https://arxiv.org/html/2510.07488), while [persona ensembles did better on behavioral prediction](https://behavior-in-the-wild.github.io/social-agents.html). The later experiment should test for an effect in either direction, and by task type. Both results come from search summaries.
- **MAST is useful framing.** [It lists inter-agent misalignment as a failure category](https://arxiv.org/pdf/2503.13657) but does not measure values. This comes from a search summary.
- **Citation.** ConflictScope is now [an ICLR 2026 paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4e7673b488fe8e611e7d14987ca74ce8-Abstract-Conference.html).

## Ideas from A Roadmap to Pluralistic Alignment

The paper measures models against targets such as populations and juries, not agent against agent, so each use below is an adaptation.

- **Welfare family (section 4.3).** `w_α = ((1/n) Σ j_i^(1-α))^(1/(1-α))`, with the geometric mean at α = 1. α = 0 is the plain average and α = ∞ is the worst case. Applied to pairwise agreement `1 - D_ij`, it shows whether one bad pair is driving a group. Needs no new runs.
- **Shuffle baseline (Appendix B).** Shuffle each agent's choices within each value pair and recompute `D_ij`. This separates agents favoring different values overall from agents differing on specific scenarios. Needs no new runs.
- **Soft disagreement (section 3.3).** Jensen-Shannon distance per scenario on A/B probabilities, averaged across scenarios. Needs code changes, and models that return logprobs.
- **Limitation (sections 4.2 and 4.3).** Trade-off and welfare functions assume values can be compared on one scale. Euclidean distance over 8 equally weighted values assumes the same thing.
