# Implementation plan: group goal-distance tool on ConflictScope (for Claude Code)

Nov 6, 2026

## Mission, constraints, non-goals

**Mission.** Build a small tool on top of the open-source ConflictScope repo (https://github.com/andyjliu/conflictscope, main at 86a2aa2) that takes N configured agents and reports, from one shared set of assay scenarios: (a) the N x N matrix of pairwise goal distances, (b) each agent's divergence from the other N-1 taken as a whole, and (c) the group's overall dispersion, all with paired-bootstrap intervals. Then run five validation checks (G1 to G5, section 6) that show whether those numbers can be trusted.

**Why.** The numbers are the predictor for a later experiment (not this task): do swarms of agents whose goals are far apart, measured before the swarm runs, do worse or cost more on tasks with ground truth? Everything here is a means to a clean, validated predictor.

**Hard constraints.**

- The assay must not contain swarm or multi-agent scenarios. The predictor has to be independent of the later outcome, and the agent must not be able to tell it is being assessed. Use only ConflictScope's shipped scenarios (Personal-Protective value set).
- Every agent answers the same scenarios with the same cached opening messages.
- Do not modify the shipped data files under `data/`. Write all new outputs elsewhere.
- Preexisting ConflictScope code must stay clearly separated from new code (hackathon rules: only work done during the weekend counts, and prior work must be labeled). Put new code in a new top-level directory and keep edits to `src/` minimal and listed.
- No GPU. Never route to local vLLM.
- Look things up in the code before assuming; where this plan says "verify", read the file.

**Non-goals.** Running swarms, MAST labeling, new scenario generation, any claim about swarm performance, a web UI.

**Deadline context.** Hackathon submission is due Sun Nov 8, 11:59 PM AoE. Prefer a working end-to-end path early over completeness; work items below are ordered so each leaves a runnable state.
