# 2026-10-09: Board update from the starting plan, plus adversarial review

Requested by the maintainer: rename context to Chimken, update the board from the starting plan, fan out an adversarial review of the board and the architecture, and annotate the change plan. The maintainer's rule: GitHub is the single source of truth for code, and the GitHub Project is the state management shared across agent harnesses.

## Change plan, as executed

1. Read the repository, the private starting plan and issues #1 to #13. Project 2 itself could not be read. This session's GitHub tools have no Projects v2 API, and earlier sessions recorded that the available CLI credential lacked the `project` scope.
2. Drafted about 30 items with fields and acceptance criteria.
3. Ran four independent adversarial reviews before creating anything. The reviews covered hosting and resilience, secrets and privacy, the board as shared state, and board quality. The report is in [the review](../reviews/2026-10-09-adversarial-review.md).
4. Revised the draft with the findings, then created issues #18 to #46. Each carries labels, a `## Planning` block, acceptance criteria, dependencies and a provenance line naming the findings behind it. Household specifics were kept out because this repository is public.
5. Linked the new issues as native sub-issues: #18, #19, #24 and the Phase 0 epic #25 under #11. #20 to #23 and #46 under #1. #45 under #3. #26 to #37 under #25, and #39 to #44 under the new Phase 1 epic #38.
6. Added change notes as comments on #1, #7 and #11.

## Labels added

`priority:P0`, `type:decision`, `phase:0` and `phase:1`. GitHub created them automatically when the first issue used them, so they still need descriptions and colors. Size is kept in issue bodies until #20 settles the field set.

## Why the plan changed from the first draft

- Every Phase 0 and Phase 1 item now waits on decisions #18 (hosting approval) and #19 (public/private boundary). This keeps the work consistent with README, `docs/architecture.md` and #11.
- Backups and a passed restore drill (#32, #33) are hard blockers for real household data.
- The second adult's buy-in became work items: a kickoff that blocks deployments (#39), consent (#27), degraded mode (#36) and an adoption gate (#42).
- The "suggested harness" field was dropped because it conflicts with ADR 003.
- Phase 2 to 4 placeholders became a "Later" list in #38 instead of issues.
- Deploy automation and ops CI were merged into one deferred item (#37). The dashboard and reverse proxy were also deferred.

## Proposed, not applied (needs the maintainer)

- Pause #2, #4, #6, #10 and #13 at P2 while Phase 0 and 1 run.
- Raise #11 to P1 once #18 is accepted, and widen #12 to cover VM cost and workload.
- Add one sentence to #7 limiting it to agent workflow rehearsal.
- ~~Create the private operations repository recommended in #19.~~ Dropped after the invariant change below.
- Configure Project 2 fields, views and built-in workflows (#22). This needs a `project`-scoped credential that this session does not have.

## Not changed

No existing issue was closed, deleted or relabeled. No Project fields, views or memberships were touched. The Project's auto-add workflow is unconfirmed, so new issues may not appear on the board until #22 is done or they are added by hand.

## Later on 2026-10-09: plan invariant change

The maintainer changed the plan invariants. The repository is public and stays public, and planning, execution and operations may all live in it. Protection moves from repository visibility to a data isolation layer: GitHub Projects for task state, Notion and Google Drive for personal information, host filesystems and SQLite or Postgres for app data, and possibly other connected sources. Sensitive information belongs in that layer, never in the repository.

What changed in response:

- Recorded the invariant as [ADR 004](../adr/004-public-repository-and-data-isolation.md) and added it to `AGENTS.md` and `docs/architecture.md`. Hosting approval (#18) moves from ADR 004 to ADR 005.
- Rewrote #19 from "public/private boundary, recommend a private `chimken-ops` repository" to "ADR 004: public repository with a data isolation layer". The private repository idea is dropped.
- Widened #27 into data classification plus a store map, so every data class has a home in the data layer.
- Raised #24 (content scanning) to P0 and extended it to issue and PR text, because scanning is now the main safety net.
- Added #48 (operations config in `ops/` with placeholders resolved from the data layer), #49 (data-layer access boundaries per harness and connector) and #50 (backups of the hosted data-layer stores).
- Edited #18, #20, #22, #23, #25, #28 to #32, #35, #37, #38, #40, #43, #44 and #46 so they point at `ops/` and the data layer instead of a private repository. #37 now deploys from this repository, using a protected environment that agent workflows cannot reference, and keeps configuration out of public logs.
- Struck through the outdated parts of the change note on #11, and added a note on #1.
- Re-evaluated the review findings that depended on a private repository; see the re-evaluation section of [the review](../reviews/2026-10-09-adversarial-review.md).

Kept as is: issues still describe capability rather than household specifics, because issue text in a public repository is public. The difference now is that the specifics have a defined home in the data layer.

The maintainer's private starting plan, which lives outside this repository, was revised the same day to match ADR 004. Its private-repo wording became the public `chimken` repository plus the data isolation layer. It now uses `docs/decisions/` and `ops/` with placeholders. Secrets are never kept in Git, and agents never run on the live host.

## Later on 2026-10-09: SuperGrok added as an AI capability

The maintainer now has a SuperGrok (xAI Grok) subscription alongside Claude, ChatGPT/Codex and Gemini. The README already listed Grok among the harnesses that share `AGENTS.md`. What changed:

- `docs/context.md` lists the four AI subscriptions, and `docs/board.md` names Grok among the harnesses sharing board state, with every capability cell unverified.
- Issues #20 and #49 add Grok to their capability and access matrices, and their criteria now verify Grok's access the same way as the other harnesses'. #26 and #27 cover four vendor accounts instead of three. #23 adds Grok's instructions and the paste-back habit. #46 adds a Grok usage boundary until its integrations are verified.
- The private starting plan's AI subscription section now has a SuperGrok row and a Grok side for context sync.

No Grok capability was assumed. There is no `GROK.md` adapter, because Grok's discovery convention for repository instructions is unverified; #46 decides whether one is needed.
