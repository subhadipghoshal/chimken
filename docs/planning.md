# Planning

GitHub Issues are the canonical work records. [Chimken HQ | The Grand Coop](https://github.com/users/subhadipghoshal/projects/2) is the existing planning Project. Do not create a replacement Project.

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

Project 2 is linked to `subhadipghoshal/chimken`, and all 13 bootstrap issues
are present. The live configuration was verified on 2026-10-08 with the
`project`-scoped GitHub CLI credential.

| Field | Values |
| --- | --- |
| Status | Existing options preserved: Todo, In progress, Done |
| Work type | Epic, Feature, Bug, Research, Experiment, Maintenance |
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

The live Project also retains the existing Current iteration and My items
views. GitHub reserves the exact custom field name `Type`, so the equivalent
single-select field is named `Work type`. The Experiments view filters
`label:type:experiment OR label:type:research`; Agent Queue filters
`is:open label:execution:agent`. No existing Project content was deleted or
rewritten. Package manifests remain at version `0.1.0`; no registry or GitHub
release publication was authorized or performed. Do not store access tokens in
Git or public issues.

Start with the evaluation baseline and one useful workflow. Keep paid calls disabled until a maintainer sets a budget, and record operational feedback before expanding infrastructure or autonomy.
