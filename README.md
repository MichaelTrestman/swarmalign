# SwarmAlign

SwarmAlign measures the degree of value misalignment between pairs of AI agents.

It is a hackathon project built on [ConflictScope](https://github.com/andyjliu/conflictscope).

Given N agents to compose a swarm, the tool will report:

- the N x N matrix of pairwise value misalignment
- each agent's divergence from the aggregate value vector of the other N-1 agents
- the group's overall dispersion


See [implementation plan](plan.md).

## Why

Alignment is often discussed as if it were a well defined, measurable relationship between two parties, and as if all humans were approximately aligned with each other. Both assumptions are dubious. Alignment differs between humans, organizations, and AIs, and it can change over time. An agent's alignment is also not identical to that of any of its component models.

Conceptually, misalignment is something like a measure of distance between two vectors in relative goal strength space. Before we can solve "the alignment problem for AI," we need to be able to assay different agents' vectors and measure the distance. SwarmAlign will attempt that measurement for configured AI agents.

These numbers are meant to be the predictor for a later experiment: do swarms of agents whose goals are far apart, measured before the swarm runs, do worse or cost more on tasks with ground truth? That experiment is out of scope here.

The full motivation and source quotes are in [docs/why.md](docs/why.md).

## Prior work and new work

Everything through commit `86a2aa2` is ConflictScope, by Andy Liu and coauthors: `src/`, `scripts/`, `data/`, `value_sets/`, `requirements.txt`, and `LICENSE`. New work is `docs/`, `plan.md`, this README, and `.gitignore`. The upstream README is at [README.conflictscope.md](README.conflictscope.md).

## Credit and license

SwarmAlign is built on ConflictScope, from [Generative Value Conflicts Reveal LLM Priorities](https://www.arxiv.org/abs/2509.25369). ConflictScope is MIT licensed, and its [LICENSE](LICENSE) is retained here.

```
@article{liu2025generative,
  title={Generative Value Conflicts Reveal LLM Priorities},
  author={Liu, Andy and Ghate, Kshitish and Diab, Mona and Fried, Daniel and Kasirzadeh, Atoosa and Kleiman-Weiner, Max},
  journal={arXiv preprint arXiv:2509.25369},
  year={2025}
}
```
