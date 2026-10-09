# Planning

GitHub Issues are the canonical work records. [Chimken HQ | The Grand Coop](https://github.com/users/subhadipghoshal/projects/2) is the existing planning Project. Do not create a replacement Project.

## 2026-10-09 update

Issues #18 to #50 add the starting plan's decision gates, Phase 0 hosting foundation (#25) and Phase 1 household domains (#38). The change log is [docs/decisions/2026-10-09-board-update.md](decisions/2026-10-09-board-update.md), the review is [docs/reviews/2026-10-09-adversarial-review.md](reviews/2026-10-09-adversarial-review.md), and the proposed board state model is [docs/board.md](board.md). Current state lives in [docs/context.md](context.md). Sensitive task detail belongs in the data layer, not in public issues ([ADR 004](adr/004-public-repository-and-data-isolation.md)).

## Bootstrap backlog

The epics and starter issues below are live. Starter tasks are linked as native sub-issues and in the epic checklists.

| Workstream | Epic | First experiment or task |
| --- | --- | --- |
| Coop orchestration | [#1](https://github.com/subhadipghoshal/chimken/issues/1) | [Compare harness handoffs #2](https://github.com/subhadipghoshal/chimken/issues/2) |
| Knowledge and memory | [#3](https://github.com/subhadipghoshal/chimken/issues/3) | [Compare storage options #4](https://github.com/subhadipghoshal/chimken/issues/4) |
| Evidence and evaluations | [#5](https://github.com/subhadipghoshal/chimken/issues/5) | [Evaluate existing tooling #6](https://github.com/subhadipghoshal/chimken/issues/6), [blinded rubric #13](https://github.com/subhadipghoshal/chimken/issues/13) |
| Family workflows | [#7](https://github.com/subhadipghoshal/chimken/issues/7) | [Rehearse one useful workflow #8](https://github.com/subhadipghoshal/chimken/issues/8) |
| OSS contributions | [#9](https://github.com/subhadipghoshal/chimken/issues/9) | [Evaluate watcher and triage #10](https://github.com/subhadipghoshal/chimken/issues/10) |
| Infrastructure | [#11](https://github.com/subhadipghoshal/chimken/issues/11) | [Measure local workload and cost #12](https://github.com/subhadipghoshal/chimken/issues/12) |

Area, type, priority, and execution labels make the backlog usable independently of Project access. `execution:agent` indicates a bounded task suitable for a separately authorized agent run. It does not grant credentials or start execution.

## Project setup status

At bootstrap, repository access was verified, but the available GitHub CLI credential lacked the `project` scope and could not read or update Project 2. The items, fields, and views below are the intended configuration; they are not claimed as configured.

| Field | Values |
| --- | --- |
| Status | Preserve existing options; target Todo, In Progress, Review, Done |
| Type | Epic, Feature, Bug, Research, Experiment, Maintenance |
| Area | Orchestration, Knowledge, Evaluation, Workflows, OSS, Infrastructure |
| Priority | P0, P1, P2, P3 |
| Execution | Human, Agent, Collaborative |

| View | Layout and purpose |
| --- | --- |
| Backlog | Table of open work |
| Board | Board grouped by Status |
| Roadmap | Epics; use roadmap dates only when there is an actual schedule |
| Experiments | Experiments and research, with explicit evidence and stop conditions |
| Agent Queue | Open `execution:agent` tasks, with issue-defined scope and validation |

To finish setup, authorize GitHub CLI with `gh auth refresh -h github.com -s project`, then link this repository, add the existing issues, and apply the fields and views while preserving existing Project content. Update this status after verifying the live configuration. Do not store access tokens in Git or public issues.

Start with the evaluation baseline and one useful workflow. Keep paid calls disabled until a maintainer sets a budget, and record operational feedback before expanding infrastructure or autonomy.
