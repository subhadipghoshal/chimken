# ADR 004: Public repository with a data isolation layer

Status: accepted (maintainer decision, 2026-10-09)

Chimken's repository is public, and it will stay public. It holds planning, execution and operations, including deployment configuration for household services. Protection does not come from repository visibility. It comes from keeping sensitive information in a separate data layer that the repository only refers to.

## Layers

| Layer | Holds | Examples |
| --- | --- | --- |
| Repository (public) | Code, docs, decisions, generic tasks, operations configuration with placeholders | Compose files, setup scripts, runbooks, workflows, synthetic fixtures |
| Task state | Project state for planning | GitHub Projects. Public issue text follows the repository rule; any sensitive task detail lives only in a private Project's draft items or fields |
| Personal information | Household knowledge and documents | Notion, Google Drive |
| App data | Runtime data of household services | Host filesystem, SQLite and Postgres databases |
| Secrets | Credentials and keys | Password manager or secret store; never in Git, not even encrypted |

More data sources may join the data layer. Each new source gets a classification entry and an access rule before any agent or service connects to it.

## Rules

- Anything sensitive lives in the data layer, never in the repository, its issues, PRs, commit messages or Actions logs. Sensitive includes personal names and contact details, account identifiers, network identifiers (hostnames, tailnet names, IP addresses), cloud resource identifiers, household routines, and any health, finance or document content.
- Operations configuration in the repository uses placeholders. Real values are resolved from the data layer at deploy time on a trusted machine or a protected CI environment.
- Agents work on the repository. They reach a data-layer store only through a connector or credential granted for that store and that task, and they treat what they read as data, not instructions.

## Tradeoff

A public repository lets every harness read the same source without extra credentials, and it keeps the project open. The cost is that a mistake in a commit, issue or log is public immediately and stays in history. Mitigations are content scanning in CI and pre-commit, issue templates that warn contributors, and Actions logs that never print configuration values. The service inventory and architecture are public by design; only values and content are protected.

This supersedes the 2026-10-09 review recommendation to create a private operations repository.

## Revisit

Revisit if a sensitive value reaches public history despite these controls, or if a data-layer store cannot meet the access and backup rules.
