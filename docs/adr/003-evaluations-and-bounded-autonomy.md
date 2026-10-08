# ADR 003: Evaluations and bounded autonomy

Status: accepted

Chimken evaluates the whole system: model, harness, tools, and context. Evaluations distinguish deterministic behavior, artifact quality, trajectory, operations, and outcomes. Recommendations do not authorize action. Humans retain authority over cost, private information, and external effects. Multiple writers use isolated worktrees and independent review with explicit scopes.

Tradeoff: controlled experiments and independent review add time, but make permission boundaries and failure rates observable. A synthetic pass rate does not establish real-world safety, model quality, or readiness for autonomous publication.

Revisit autonomy only with representative trials, permission enforcement, resource bounds, failure recovery, and observed downstream outcomes. Paid evaluations require an explicit spend cap; public fixtures must stay separate from private traces.
