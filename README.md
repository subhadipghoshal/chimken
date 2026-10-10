# Chimken

Chimken, formerly Arohan, is an Apache-2.0, family-first AI experimentation
and automation modular monorepo. We learn from operational outcomes while
respecting cost, human time, and the boundary between public code and private
life.

The first runnable slice is deliberately small: an offline Python 3.12+ `uv`
workspace. `chimken-oss-triage` is a pure policy package. `chimken-lab` is a
CLI that evaluates 18 synthetic OSS-triage cases. It makes no network requests
or model calls. Its reported `model_calls` and `model_cost_usd` are zero; the
only cost is local compute.

```sh
uv sync --all-packages --locked
uv run --all-packages --locked chimken-lab triage workflows/oss-contributions/example.json
uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks, the
[OSS-triage contract](docs/contracts/oss-triage.md) for input and output
schemas, and [docs/architecture.md](docs/architecture.md) for boundaries.

The [bootstrap handoff](docs/handoffs/2026-10-08-bootstrap.md) records the
historical integrated checkpoint, agent work, verification, and remaining
review and publication steps.

## What Chimken is building

Organize work by capability, not by model or provider. The shared boundary is
one directional: `chimken-lab` depends on `chimken-oss-triage`. There is no
generic shared package.

Coop is a future coordination subsystem. Git is the source and architecture,
not a runtime knowledge database. Private household data, secrets, runtime
state, and external OSS clones stay outside this repository.

No provider service, live agent runner, network watcher, state database, or
cloud provisioner is implemented. Future candidates for evaluation include
Inspect AI, gh-aw, OpenSWE, CrewAI, LangGraph, Orca and Jev (#51). Mentioning
them is not a claim of current support or a selection decision. Kubernetes,
cloud, and a homelab come only after a workload proves the need.

## Collaboration

Use concise canonical [AGENTS.md](AGENTS.md) guidance, with scoped guidance in
`apps/`, `packages/`, and `evals/`. Claude, Codex, Gemini, Grok, and future
harnesses share those instructions. The adapter files point to the canonical
guidance only; they do not promise automatic harness discovery.

For multiple writers, use isolated worktrees, give each writer an explicit
scope, and obtain independent review. Humans retain decisions involving cost,
private data, or external effects. GitHub Issues are the canonical task record.
The existing [GitHub Project](https://github.com/users/subhadipghoshal/projects/2)
organizes work, with current setup status recorded in the [planning map](docs/planning.md).

Small coop. Big ambitions. 🐣
