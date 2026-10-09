# Current context

Last verified: 2026-10-09

Read this page, `AGENTS.md` and `docs/decisions/` before starting work. This page holds only what the board cannot: what exists, what is decided, and what is open.

## What exists

- This public repository, with an offline Python workspace (`chimken-lab`, `chimken-oss-triage`) and passing CI. See the README.
- Issues #1 to #46. Issues are the work records, and [Project 2](https://github.com/users/subhadipghoshal/projects/2) organizes them. The Project's fields and views are not configured yet (#22).
- No household services, hosts or deploy paths exist yet.

## Decided

- GitHub is the single source of truth for code. The GitHub Project is the shared state across harnesses. How that works in practice is proposed in `docs/board.md` and decided in #20.
- Live household services are planned as a separate plane from the experiment monorepo. Nothing starts until #18 and #19 are accepted.

## Open questions

- #18: Approve free-tier cloud hosting, the budget cap and recovery targets?
- #19: Should household operations config and household issues live in a private repository?
- #20: Which layer is authoritative for each piece of board state?
