# Adversarial review: board and architecture, 2026-10-09

Four independent reviewers were each asked to break the plan, not approve it. They read the private starting plan, a draft of the board update, and this repository. Each reviewer covered one lens:

| Lens | Question it attacked |
| --- | --- |
| Hosting and resilience | What happens when the free-tier VM, an account or the one operator disappears? |
| Secrets and privacy | What leaks through a public repository, CI, AI vendors or the board itself? |
| Board as shared state | Can three vendors' harnesses really share state through a GitHub Project? |
| Board quality | Are the items complete, verifiable, sequenced and achievable at about 5 hours a week? |

The reviewers produced 49 findings: 9 critical, 19 high, 16 medium and 5 low. Overlapping findings are merged below. Vendor facts the reviewers could not check are marked "verify" in the issues and must be confirmed before anyone relies on them.

## Critical findings

| Finding | Disposition |
| --- | --- |
| The draft contradicts repository policy. README, `docs/architecture.md` and #11 defer cloud work until scope and budget are approved, and #7/#8 are synthetic-only. | #18 (ADR 004) must approve hosting before any Phase 0 work starts. Change notes were added to #7 and #11. |
| The board is a leak channel. The repository is public, so issues naming regions, network ACLs, household routines or interviews expose the household. | #19 (ADR 005) sets a public-content policy and recommends a private operations repository. All new issues use generic wording. |
| The cloud account is the whole platform, and there is no recovery target or non-Oracle fallback. | Recovery targets are set in #18. A timed rebuild on a fallback host is #35. |
| Recovery keys can be lost along with the systems they recover. | Break-glass kit that both adults can open: #31. |
| `@claude` on a public repository turns anyone's issue text into agent input while the agent holds write access. | #46 (OWNER-only triggers, no deploy secrets in this repository) and #21 (untrusted label, input-as-data rule). |
| Agents can effectively approve their own work, because there is no branch protection or CODEOWNERS and "Closes #n" auto-closes the issue. | #21: required human approval, CODEOWNERS on workflows, and agents never set Done. |
| Few harnesses can write Project v2 fields, so "board as shared state" means one writer in practice. | #20 (ADR 006) picks the authoritative layer and builds a per-harness capability table. Proposal: `docs/board.md`. |
| "Backups before data" was a guardrail but not a dependency. | Every Phase 1 deployment is blocked by #33 (restore drill). |

## High findings

| Finding | Disposition |
| --- | --- |
| Pay As You Go is effectively required to avoid idle reclamation, and a budget alert does not cap spending. | #18 and #28 (quotas, fallback for capacity) |
| Monitoring and backup checks die with the host. | #34 (external heartbeat, alerts not routed through the host) |
| Backups can be deleted by a compromised host, and live database copies restore corrupted. | #32 (append-only credential, app-level dumps) |
| The local backup copy depends on the laptop being awake. | #32 (second copy, or a dated gap) |
| Only one person can operate the platform. | #36 (degraded mode), #30 (second admin), #26 |
| The deploy credential is effectively root on a host that holds finance data. | #37 (private repository, forced-command user, environment approval), deferred to P2 |
| There is no consent or data classification for the second adult's data. | #27 |
| LLM and MCP egress paths for finance and health data are unguarded. | #27 (paid no-training key or local model, read-only MCP) |
| Key loss and key theft are conflated. | #31 and #32 |
| Agents may end up running next to live data. | #23 (AGENTS.md rule), #29 |
| Three state copies (labels, body blocks, Project fields) will drift. | #20 (precedence rule; body block informational only) |
| There is no claim or lease rule, so stale "In Progress" cards build up and agents duplicate work. | #21 |
| Two products share one board. | #18, #19, and a separate Phase 1 epic #38 |
| Decision recording is fragmented, and an append-only file causes conflicts. | `docs/decisions/` uses one file per decision; finalized in #20 |
| Adoption work is token-sized. | #39 blocks deployments; adoption gate #42; second-adult acceptance criteria in #40 |
| The plan does not fit about 5 hours a week. | Deferred items moved to P2 or the epic's "Later" list. Pausing experiments is proposed on #1; it has not been applied. |
| Several items are XL in disguise. | Budgeting is split into #43 and #44. Backups and the restore drill are split into #32 and #33. Deploy work (#37) is deferred. |
| Tasks from the starting plan are missing. | Retros (#42); habits and guardrails (#23); capacity fallback (#28) |

## Medium and low findings

| Finding | Disposition |
| --- | --- |
| Path-only repository checks miss hostnames, IP addresses, resource identifiers and emails. | #24 |
| Encryption at rest and account MFA are not covered. | #26; threat-model note in #43 |
| A public notification topic can leak alerts. | #34 |
| Identity failures are linked through one account. | #26 |
| Moving Home Assistant later is costly. | #41 defaults chores to Grocy until the home box exists |
| A "suggested harness" field contradicts ADR 003. | Dropped; #46 records the harness actually used |
| Field and label sprawl. | Phase labels only; Size kept in the body until #20 finalizes fields |
| Duplicates: context docs vs planning, Obsidian vs #4, rebuild vs #12. | #23, #45, #35 scopes adjusted |
| Phase 2 to 4 placeholders are noise. | Listed under "Later" in #38, not opened as issues |
| `context.md` will go stale. | `Last verified` date; staleness check in #23 |
| Attribution is lost when every harness uses the owner's identity. | Trailers in #21 |
| A broad `project` credential has a large blast radius. | #22 |
| A Vercel front end would break the private-network guardrail. | Out of scope until a dedicated ADR exists |
| Lock-in to GitHub Projects. | #20 requires the board to be rebuildable from issues and labels |

## What this review did not cover

The reviewers did not verify vendor terms, limits or capabilities online. Live Project 2 contents were not visible to this session, so existing board-only items (draft items not backed by issues), if any, were not reviewed.
