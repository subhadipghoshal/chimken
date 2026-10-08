# Chimken bootstrap: consolidated agent handoff

Date: 2026-10-08. This handoff preserves the historical integration checkpoint and records the verified continuation below.

## Current state

- The integrated bootstrap and packaging fix are published to existing `main` at [7b41112](https://github.com/subhadipghoshal/chimken/commit/7b41112e043c6839882ab1f5fdcb729786774e96). The earlier assimilation checkpoint is [64f22bd](https://github.com/subhadipghoshal/chimken/commit/64f22bd541c9aad53574246056902451740ca352).
- Fresh independent Terra review found no actionable findings. [Hosted CI passed](https://github.com/subhadipghoshal/chimken/actions/runs/37779614295): Quality, Python 3.12 tests, and Python 3.14 tests, including distribution license validation.
- All original writer worktrees and the packaging/handoff follow-ups have been assimilated. Worktrees remain available for inspection. No release or package registry publication was performed.
- All agent outcomes are recorded here, including the incomplete first review and the completed replacement review. The local baseline has 53 passing tests and 18 passing synthetic evaluation cases with no model calls.
- Project 2 is linked to `subhadipghoshal/chimken`, all 13 planning issues are
  present, and the documented fields and views were configured with the
  project-scoped GitHub CLI credential. GitHub reserved the exact custom field
  name `Type`, so the equivalent field is named `Work type`. Private
  vulnerability reporting, secret scanning, and push protection were
  reverified as enabled after publication.

## Historical checkpoint at 64f22bd

- Existing repository: https://github.com/subhadipghoshal/chimken
- Existing Project: https://github.com/users/subhadipghoshal/projects/2
- Integration branch: `bootstrap/chimken-foundation`.
- Original remote base: `ff74a656de7728154a7605e2ef7c9d0af1ef2d5d`.
- Local seed commit: `a92763ca1a71257f8da9a8c554c994044e447f87`.
- All four writer worktrees have been assimilated into the primary checkout. The commit containing this handoff checkpoints the integrated work. Writer worktrees remain available for inspection; they have not been deleted.
- The bootstrap code and this checkpoint have not been pushed. Remote `main` was still the original base when last checked. There is no bootstrap pull request or hosted CI result yet.
- GitHub planning issues and repository security settings have already been updated. Those external changes are listed below.
- Independent review stopped at an account usage limit without a final findings report. Do not treat its partial checks as approval.
- Continuation requested: fan out two cheap-model follow-ups, with Terra handling the packaging fix and Luna auditing this handoff. These follow-ups are pending; packaging is not marked fixed, review is not marked passed, and code is not marked published.

## User intent and architecture

Chimken, formerly Arohan, is a public Apache-2.0 modular monorepo for family-first AI experimentation and automation. Favor useful experiments, operational feedback, existing tools, open source, and cost-conscious choices over building a platform in advance. Evaluate complete model, harness, tool, instruction, and context configurations; do not permanently assign roles by model reputation.

Keep household and private data, secrets, runtime state, generated traces, databases, and external OSS clones out of Git. Use synthetic fixtures, scoped instructions, isolated writer worktrees, and independent review. The repository's original Apache license is unchanged.

The implemented slice is deliberately offline:

```text
explicit JSON facts or evaluation suite
  -> chimken-lab: input validation, CLI, evidence report
  -> chimken-oss-triage: pure deterministic recommendation
  -> JSON stdout
```

The policy recommends `ignore`, `research`, `design`, or `agent_candidate`. Every successful report explicitly says `execution_authorized: false`. It performs no network requests or model calls. No live agent executor, watcher, knowledge database, provider integration, or deployment has been implemented.

## Handoffs from all seven agents

### Runtime: Schrodinger, Sol

- Branch: `codex/chimken-bootstrap-runtime`.
- Scope: `apps/lab/src/` and `packages/oss-triage/src/`.
- Finished strict input validation, safe CLI errors, duplicate JSON field rejection, suite validation, and bounded input processing.
- Preserved the routes and reasons, with exit codes `0` for success, `1` for evaluation mismatch, and `2` for invalid or unreadable input.
- Added interpreter-version metadata without machine identifiers. Reports omit raw facts and input paths.
- Reported passing scoped Ruff, formatting, strict Mypy, the 18-case fixture, and direct success and failure probes.
- All four changed source files are assimilated without content differences from the final writer worktree.

### Tests and repository checks: Ptolemy, Sol

- Branch: `codex/chimken-bootstrap-tests`.
- Scope: `tests/` and `scripts/check_repository.py`.
- Added CLI integration tests, a dependency-direction test, and repository checks covering private paths, force-added ignored files, sensitive artifact names, gitlinks, symlinks, and files over 1 MiB.
- Repository checks use Git file inventories and do not print file contents. They are not comprehensive secret or personal-data scanning.
- Initial handoff reported 50 passing tests against the seed runtime. A later update added three argument-error cases plus interpreter-version assertions. Assimilation includes those later changes.
- Integration added `pythonpath = ["."]` to the pytest configuration so the documented `pytest` command can import the checker. CLI subprocess tests deliberately select this checkout's source paths instead of inheriting a possibly unrelated `PYTHONPATH`.
- Final integrated suite: 53 tests. The earlier formatting failures in this agent's seed checkout were resolved by the runtime agent's changes.

### Architecture and contributor documentation: Bernoulli, Terra

- Branch: `codex/chimken-bootstrap-docs`.
- Scope: README, canonical and scoped agent instructions, harness pointers, contribution and security guidance, architecture, contract, ADRs, evaluations, experiments, and OSS workflow documentation.
- Delivered 17 changed documents. All are assimilated.
- Main-agent integration expanded the capability responsibility table, ADR tradeoffs and revisit conditions, confirmed security-reporting state, and exact evaluation metadata and timing semantics.
- Main-agent integration also clarified that existing explicit task authorization persists; agents need human direction for actions beyond that scope.
- Baseline-check failures reported by this agent concerned absent tests/checker or unformatted runtime in its isolated seed checkout. The integrated candidate contains those companion changes and passes their checks.

### CI and contribution templates: Pascal, Terra

- Branch: `codex/chimken-bootstrap-ci`.
- Scope: `.github/` only; seven new files are assimilated without content differences.
- Added CI for pushes and pull requests, a Python 3.12 quality job, and a Python 3.12/3.14 test matrix.
- Uses read-only repository permissions, disabled checkout credential persistence, full-SHA action pins, timeouts, and cancellation of superseded runs.
- Added task, bug, and experiment forms, a PR template, scoped automation instructions, and monthly GitHub Actions dependency updates.
- Reported successful YAML parsing and workflow structure assertions. The main agent separately verified the supplied action SHAs against GitHub.
- Hosted GitHub Actions execution remains pending publication.

### Planning content: Lorentz, Luna

- Read-only content task; no writer worktree.
- Drafted six epics and six starter experiments or research tasks.
- Main agent refined the content, added one bounded agent task, published the issues, applied labels, and linked native sub-issues plus epic checklists.
- No replacement repository or Project was created.

### Independent review: Rawls, Sol at xhigh effort

- Read-only review of the integrated candidate against `ff74a65`, including untracked files.
- Partial progress reported that the complete change surface had been read and that 50 tests, static checks, repository checks, evaluation, lock validation, and builds passed at that point.
- The task hit an account usage limit before issuing a final review. There is no final no-findings result and no completed severity/disposition assessment.
- Saved command output confirms that the built wheels and source distributions did not contain a license file. The main agent independently confirmed the wheel omission. Resolve this packaging issue and have the final candidate reviewed before distribution.
- The later three argument-error tests and this handoff were added after the interrupted review. A resumed reviewer must inspect the final checkpoint, not assume its earlier view is complete.

### Runtime and package verification: Bohr, Terra

- Read-only verification using temporary environments outside the checkout; no source changes.
- Locked install on CPython 3.12.12 with uv 0.9.3 succeeded.
- The then-current 50-test suite passed in 4.83 seconds; the synthetic evaluation passed 18 of 18 cases.
- Built both `chimken_lab-0.1.0-py3-none-any.whl` and `chimken_oss_triage-0.1.0-py3-none-any.whl`.
- Installed exactly those two local wheels into another clean environment with `UV_OFFLINE=1` and `--no-index`.
- Confirmed imports resolved from that environment's `site-packages`, then ran the installed console entry point from outside the source checkout against a copied fixture. All 18 cases passed.
- Parsed CI YAML and checked its Python versions, permissions, and full-SHA action references.
- A follow-up request for details hit the usage limit, but the original detailed results were recovered from saved task output. Package execution passing does not resolve the separate license-file omission.

## Integration and verification evidence

The main agent audited every modified or new path in each writer worktree. No worker-owned path is missing from the integrated checkout. Documentation refinements and the test-source-path change described above are intentional integration decisions.

| Check | Result and scope |
| --- | --- |
| Ruff lint and formatting | Passed on the integrated candidate |
| Strict Mypy | Passed for both runtime packages, four source files |
| Pytest on CPython 3.14.8 | 53 passed after the final test assimilation |
| Pytest on CPython 3.12.12 | 53 passed after the final test assimilation |
| Repository policy checker | Passed on the integrated candidate |
| Synthetic evaluation | 18/18 correct; zero false agent candidates; zero model calls; zero model API spend |
| Installed-wheel execution | Passed outside the repository on Python 3.12.12 |
| Package license contents | License file absent from the inspected build artifacts; follow-up required |
| Documentation local links and punctuation | Passed before this handoff; recheck after edits |
| Whitespace/diff checks | Passed |
| Independent review | Incomplete because of the review task's usage-limit failure |
| Hosted CI | Not run yet |

Evaluation fixture SHA-256:

```text
486890a0aa03ec00265c13e0632eb6867c4b7a4b10b9080a8bbc21e821788039
```

The evaluation is a regression test of a deterministic rule set. It is not evidence of model quality or readiness for autonomous work. Timing varies between runs; the routes and reasons are deterministic. Raw test logs, temporary environments, build archives, and execution reports were kept outside the public source tree.

## GitHub work already completed

The existing repository remains public. Private vulnerability reporting was enabled and verified. Secret scanning and secret push protection were already enabled and remain enabled.

Thirteen open issues were created and verified:

| Area | Epic | Native sub-issues |
| --- | --- | --- |
| Orchestration | [#1](https://github.com/subhadipghoshal/chimken/issues/1) | [#2: compare handoffs](https://github.com/subhadipghoshal/chimken/issues/2) |
| Knowledge | [#3](https://github.com/subhadipghoshal/chimken/issues/3) | [#4: compare storage](https://github.com/subhadipghoshal/chimken/issues/4) |
| Evaluation | [#5](https://github.com/subhadipghoshal/chimken/issues/5) | [#6: evaluate tooling](https://github.com/subhadipghoshal/chimken/issues/6), [#13: blinded rubric](https://github.com/subhadipghoshal/chimken/issues/13) |
| Family workflows | [#7](https://github.com/subhadipghoshal/chimken/issues/7) | [#8: rehearse a workflow](https://github.com/subhadipghoshal/chimken/issues/8) |
| OSS | [#9](https://github.com/subhadipghoshal/chimken/issues/9) | [#10: watcher and triage experiment](https://github.com/subhadipghoshal/chimken/issues/10) |
| Infrastructure | [#11](https://github.com/subhadipghoshal/chimken/issues/11) | [#12: local workload inventory](https://github.com/subhadipghoshal/chimken/issues/12) |

Fifteen labels describe six areas, four work types, three execution modes, and two priorities. Existing default labels were preserved. Issue #13 is the scoped agent task; its label is not permission to execute other work.

Project 2 configuration is complete for the documented scope. The repository
is linked, the 13 existing issues are present, and the additive fields and
views are recorded in `docs/planning.md`. The exact custom field name `Type`
is reserved by GitHub, so the equivalent field is named `Work type`. Existing
Project content was preserved; no visibility or workflow changes were made.

## Continuation after the checkpoint

- Terra packaging worker (Copernicus) added exact Apache license copies to both package roots and `scripts/check_package_archives.py`. All four built wheel and source archives passed its content assertion. An isolated Python 3.12 installation of both wheels passed all 18 synthetic cases outside the checkout.
- Luna handoff auditor (Laplace) checked the seven original agent sections and local links, and clarified the historical checkpoint reference in this document and the README.
- The primary agent assimilated those worktrees, connected archive building and license verification to CI, and passed all 53 tests, Ruff, Mypy, repository metadata and whitespace checks. Worktrees remain available for inspection.
- Luna preflight agent (Hooke) independently confirmed 13 open issues, the original remote main commit, and the missing Project read permission. It made no external changes.
- Fresh Terra reviewer (Popper, xhigh effort, no inherited author context) reviewed the complete original-base diff plus all working-tree additions. Verdict: no actionable findings. Independent checks passed: lock consistency, Ruff, strict Mypy, 53 tests on Python 3.14, repository policy, 18-case evaluation, all four archive licenses, and an installed-wheel smoke test outside the checkout. Hosted CI and live GitHub configuration were outside this review's verification boundary.
- Hosted CI subsequently passed after publication; see Current state above. The earlier tables and checklist describe the historical checkpoint, not an assertion that the packaging omission or independent review remains unresolved.

## Historical resume checklist

1. Locate the primary checkout with `git worktree list`, select `bootstrap/chimken-foundation`, and inspect its status and this checkpoint before changing anything. Preserve unrelated work and retained writer worktrees.
2. Include the repository's Apache license in both packages' build artifacts and add a focused packaging assertion. Rebuild and inspect wheels and source distributions, then repeat the installed-wheel smoke test.
3. Obtain a complete independent review against the original base after the final fixes. Earlier partial review progress is not approval; self-review is not a substitute.
4. Re-run the documented checks, then publish the authorized bootstrap through the existing repository. Verify hosted CI on Python 3.12 and 3.14 before reporting the bootstrap complete.
5. Have the user authorize Project access with `gh auth refresh -h github.com -s project`. Inspect and preserve existing Project content, link this repository, add the existing issues, and configure supported fields and views. Do not create replacements or infer permission to change visibility.
6. Update `docs/planning.md` and this handoff with verified publication, CI, review, and Project outcomes. Report exact commit and issue links.

From the repository root, the portable check commands are:

```sh
uv sync --all-packages --locked
uv run --all-packages --locked ruff check .
uv run --all-packages --locked ruff format --check .
uv run --all-packages --locked mypy
uv run --all-packages --locked pytest
uv run --all-packages --locked python scripts/check_repository.py
uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json
```

`just check` is an optional equivalent. No paid provider calls, deployments, external OSS clones, or household-data integrations are needed for this checkpoint.
