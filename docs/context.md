# Current context

Last verified: 2026-10-09

Read this page, `AGENTS.md` and `docs/decisions/` before starting work. This page holds only what the board cannot: what exists, what is decided, and what is open.

## What exists

- This public repository, with an offline Python workspace (`chimken-lab`, `chimken-oss-triage`) and passing CI. See the README.
- Issues #1 to #50. Issues are the work records, and [Project 2](https://github.com/users/subhadipghoshal/projects/2) organizes them. The Project's fields and views are not configured yet (#22).
- No household services, hosts or deploy paths exist yet.
- AI capabilities: Claude Pro, ChatGPT Plus (Codex), Google AI Pro (Gemini) and SuperGrok (Grok, added 2026-10-09). Grok's GitHub, Projects and API access is unverified; see #20 and #49.

## Decided

- GitHub is the single source of truth for code. The GitHub Project is the shared state across harnesses. How that works in practice is proposed in `docs/board.md` and decided in #20.
- The repository is public and stays public. Sensitive information lives in the data layer: GitHub Projects, Notion, Google Drive, and host files and databases ([ADR 004](adr/004-public-repository-and-data-isolation.md)).
- Live household services are planned as a separate plane. Nothing starts until hosting is approved in #18.

## Open questions

- #18: Should we approve free-tier cloud hosting, the budget cap and the recovery targets?
- #27: Which data class goes in which data-layer store, and what may each vendor see?
- #20: Which layer is authoritative for each piece of board state?
