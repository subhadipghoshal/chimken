# Architecture

Chimken is a public, Apache-2.0 modular monorepo for family-first experimentation and automation. Its architecture evolves from useful work, observed failures, and operating cost. Reuse an existing tool, measure it on a real task class, and build only the missing capability.

## Implemented slice

```text
explicit local JSON
    -> apps/lab (validation, command line, evaluation report)
    -> packages/oss-triage (pure recommendation policy)
    -> JSON on stdout
```

The dependency is one way: `chimken-lab` imports the public `chimken_oss_triage` interface. The policy owns facts, routes, decisions, and deterministic recommendations. It has no I/O or runtime dependencies. The lab owns file loading, bounded input handling, evaluation metrics, and exit codes. An architecture test prevents the policy from importing outer layers.

Both components are real installable workspace members with a shared lockfile. They are not separate deployed services. Only create another module when a concrete behavior needs an owner; a generic shared package is not justified.

## Capability boundaries and next experiments

| Capability | Responsibility | Boundary and next evidence |
| --- | --- | --- |
| Coop orchestration | Coordinate tasks, harness handoffs, budgets, and review | Future. Compare existing harnesses and orchestration tools on the same public task before selecting an adapter. A model never grants its own authority. |
| Knowledge and memory | Curated context, provenance, retention, retrieval, and deletion | Future. Evaluate simple files plus SQLite metadata against existing tools on a synthetic corpus. Source control is not the knowledge database. |
| Evaluations | Measure configuration, artifacts, trajectories, economics, and outcomes | The current CLI checks 18 synthetic triage cases. Reuse evaluation tooling for broader trials; retain separate quality and cost dimensions. |
| Workflows | Compose capabilities into useful family and research tasks | Future. Start with one read-only rehearsal, explicit review points, and measurable human effort saved. |
| OSS contributions | Observe repositories, normalize issues, triage, prepare work, and learn from review | Only offline recommendation is implemented. Watchers, deduplication, isolated execution, publication, and PR monitoring remain later steps. |
| Infrastructure | Reproducible environments, observability, artifact retention, and operating limits | Current: local uv tooling and CI. Cloud, containers, Kubernetes, and homelab services require a measured workload and budget. |

Inspect AI, gh-aw, OpenSWE, CrewAI, and LangGraph are candidates for evaluation, not selected dependencies. Harness roles are hypotheses to test, not permanent assignments based on provider reputation. The same comparison records model, harness, tools, skills, context, instructions, limits, and human corrections.

## Public source and private operation

Git stores source, small curated synthetic fixtures, public configuration, and reviewed architecture decisions. Household content, emails, medical or financial records, credentials, execution state, raw traces, databases, and large generated artifacts stay in access-controlled storage outside this checkout. External OSS projects use their own repositories and isolated workspaces.

Ignoring a path is an accident-prevention measure, not an access-control boundary. A future live connector needs scoped credentials, explicit data access and retention, bounded retries and cost, and a separate authorization check before side effects. Retrieved text is data, not instructions. The current `agent_candidate` route is only a suggestion for reviewed planning.

## Learning and promotion

Use the [experiment template](../experiments/README.md) to record a hypothesis, simplest baseline, budget, success criteria, adverse cases, and operational feedback. Prefer deterministic logic or conventional ML when it meets the need more cheaply than an LLM. Promote a successful experiment by giving it an owner, documented interface, tests, failure behavior, and an ADR. Stop or archive experiments without a useful result. Conflicting experiments may keep independent environments instead of forcing incompatible dependencies into the shared workspace.

GitHub issues are the canonical work records; the existing Project provides views of the same work. See the [planning map](planning.md). Multiple writers use isolated worktrees, scoped context, explicit handoffs, and independent review. Split repositories only for real ownership, visibility, lifecycle, or measured tooling constraints.

## Decisions

- [ADR 001: modular monorepo and data boundary](adr/001-modular-monorepo-and-data-boundary.md)
- [ADR 002: runnable offline baseline and reuse](adr/002-runnable-offline-baseline-and-reuse.md)
- [ADR 003: evaluations and bounded autonomy](adr/003-evaluations-and-bounded-autonomy.md)
