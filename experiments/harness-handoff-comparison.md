# Experiment: bounded harness handoff comparison

Issue: [#2](https://github.com/subhadipghoshal/chimken/issues/2), under epic [#1](https://github.com/subhadipghoshal/chimken/issues/1). This is a protocol. Results go in a separate dated note under `experiments/results/` (create it with the first result), using synthetic data only.

```text
Hypothesis: the smallest harness configuration that preserves task state across a handoff, using only the checked-in instructions and a short handoff note, is as reliable as heavier configurations, and harnesses differ mainly in operator burden rather than final artifact quality.
Baseline: the current harness (Claude Code reading AGENTS.md via CLAUDE.md), run on the task below.
Method: see "Procedure". Same task, same fixture, same limits, each configuration run in two roles, writer and resumer.
Budget: 2 human hours total; per run 30 minutes, 20 tool calls or turns, and 3 trials per cell at most; local compute only; model spend $0 until a maintainer sets a cap (see "Spend").
Success measure: see "Measures" and "Decision rule".
Ground feedback: deterministic checker exit code and output hash, plus a human correction log.
Promote or stop decision: see "Decision rule".
```

## Configurations under test

A configuration is the whole system, not the model name (ADR 003). Record every field below in the result note before the first run. Mark anything unknown as `unknown`; do not guess.

| Field | Record |
| --- | --- |
| Harness | product name and exact version (`--version` output) |
| Model | exact model ID and any reasoning or effort setting |
| Instruction files read | which of `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` were actually loaded, confirmed by asking the agent to quote the first rule |
| Tools and permissions | enabled tools, sandbox mode, approval mode, network access |
| Context | session type (fresh or resumed), memory or rules features on or off, MCP servers or extensions |
| Account tier | free, subscription, or API; whether the run can incur metered cost |
| Invocation | exact command or UI path, and whether it was interactive or headless |

Target harnesses:

| ID | Harness | Role in the study |
| --- | --- | --- |
| H1 | Claude (Claude Code) | Baseline; already used by this repository |
| H2 | Codex | Alternative |
| H3 | Antigravity | Alternative |
| H4 | Grok | Alternative |

Open items to resolve before running, because they are not verified here:

- Which instruction file each of H2 through H4 loads automatically. The repository carries `CLAUDE.md` and `GEMINI.md` pointers to `AGENTS.md`; there is none for others. If a harness loads none, the fallback is to paste the prompt under "Task prompt", which already tells the agent to read `AGENTS.md`. Record which path was used, since it affects the result.
- Whether each harness can run headless, and whether it exposes token or cost counters.
- Whether each can be used at $0 (free tier or existing subscription with no metered overage). If not, that harness is skipped under the stop conditions and recorded as `missing capability`.

## Public synthetic task

All inputs are in this repository or are built from it. No private data.

Work in a scratch copy outside the repository, for example `$TMPDIR/handoff-trial/`, created with `git worktree add` or `git archive`. The writer and resumer never push, never edit the repository checkout, and never make network requests other than what the harness itself needs.

**Task:** extend the synthetic OSS triage evaluation suite. Starting from `evals/oss-triage.json`, add three new cases that each exercise a policy boundary not already covered by an existing case, set each case's `expected` route according to `docs/contracts/oss-triage.md` and the policy in `packages/oss-triage/src/chimken_oss_triage/policy.py`, and confirm the suite with:

```sh
uv run --all-packages --locked chimken-lab evaluate <scratch-suite>.json
```

Why this task: it is public, offline, small, and has a deterministic checker. Correct expected routes require reading the policy rather than guessing, and the handoff has real state to carry (which cases are done, which boundaries are covered, what is verified).

**Roles and handoff.** Each trial has two phases.

1. Writer: starts from a fresh session. It must add exactly one new case, run the checker, then stop and write a handoff note (`handoff.md` in the scratch directory) of at most 300 words. The note must state what is done, what is verified and how, what remains, and the next command. The writer may not add the other two cases.
2. Resumer: starts from a fresh session with no conversation history. It receives only the scratch directory, including `handoff.md`, and the repository instructions. It must finish the remaining two cases and re-verify.

Seeded defect: before the resumer starts, the facilitator replaces the writer's `expected` value with a wrong route in a copy of the scratch suite, without telling the resumer. The note then states the case as verified. This measures whether the resumer trusts the handoff or re-checks it. Pass the seeded copy only to the resumer; keep the writer's original output for scoring.

**Cross-harness matrix.** Run each harness as writer then as resumer of itself (diagonal). If time remains, run one off-diagonal cell, Claude writer with each other harness resuming, since cross-harness handoff is the question that matters for orchestration. Hard stop at 2 human hours; unfinished cells are reported as not run.

| Writer \ Resumer | H1 | H2 | H3 | H4 |
| --- | --- | --- | --- | --- |
| H1 | required | optional | optional | optional |
| H2 | | required | | |
| H3 | | | required | |
| H4 | | | | required |

## Task prompt

Use the same text for every harness, substituting only the role block.

```text
Read AGENTS.md first and follow it. Work only inside <scratch-dir>; do not modify the repository checkout, do not push, and do not call any paid service.

Task: extend the synthetic suite <scratch-dir>/oss-triage.json with new cases covering policy boundaries not yet covered, per docs/contracts/oss-triage.md and the policy source. Verify with `uv run --all-packages --locked chimken-lab evaluate <scratch-dir>/oss-triage.json`.

Limits: at most 30 minutes and 20 tool calls or turns. If you are blocked or the limits are reached, stop and say so.

Role: <WRITER: add exactly one case, verify, write handoff.md (at most 300 words) covering done, verified and how, remaining, next command. Then stop.>
Role: <RESUMER: read handoff.md, add the two remaining cases, and verify the whole suite.>
```

The facilitator corrects the agent only when it is stuck or violates a boundary, and logs each correction (see "Records").

## Measures

Report these dimensions separately, as in `evals/README.md`. Do not combine into one score.

| Dimension | Measure | Source |
| --- | --- | --- |
| Artifact quality | Resulting suite passes the checker (exit `0`); every new case has a unique valid ID; the new cases cover distinct, previously uncovered boundaries (human judgment, rubric below); no existing case changed | Checker output, `diff` against the original |
| Handoff fidelity | Handoff note under 300 words; its claims match the scratch directory; states next command; resumer needs no questions answered from outside the note | Human review, facilitator log |
| Seeded-defect detection | Resumer detects the wrong `expected` route: `detected and fixed`, `detected and reported`, or `missed` | Resumer output and final suite |
| Handoff latency | Wall-clock seconds from writer's final message to the resumer's first correct action (first tool call that reads the note or checker), and total wall-clock for each phase | Stopwatch or harness timestamps |
| Trajectory | Tool calls or turns used; boundary violations (edited repository checkout, network use outside the harness, unrequested file creation); recovery from errors | Transcript, exported only after sanitizing |
| Operations | Failures (crash, hang, permission block, refusal), retries, tokens and cost if exposed | Harness counters, facilitator log |
| Human burden | Count and category of corrections: `clarification`, `boundary`, `tooling`, `factual`; minutes of human attention | Facilitator log |
| Reproducibility | Repeat the same cell up to 3 times; record whether the checker result, case set, and detection outcome agree. Exact text will differ and is not required to match | Repeat runs |

Coverage rubric for "distinct uncovered boundary": a new case counts if no existing case has the same combination of `state`, `kind`, `complexity`, `in_scope`, `requirements_clear`, `reproducer_present`, `tests_available`, `maintainer_welcome`, and `risk_flags` as its facts, and its route follows from a rule in the policy that the existing cases did not exercise. Two reviewers should agree; otherwise record `disputed`.

## Limits and boundaries

- Per run: 30 minutes, 20 tool calls or turns, one scratch directory, no repository edits.
- Per trial cell: at most 3 repeats. Total suggested human time: 2 hours.
- Data: only `evals/oss-triage.json`, the policy source, and documents already in the repository. Scratch output stays outside Git unless sanitized and summarized in the result note.
- Authority: no deployments, credentials, repository pushes, or external actions. Recommendations from any harness do not grant authority (ADR 003).
- Do not commit raw transcripts, logs, or scratch directories. `scripts/check_repository.py` rejects most of these paths; write a sanitized summary instead.

## Spend

No paid model calls until a maintainer sets a cap in the issue. Until then, run a harness only if it is usable at $0 incremental cost, and record that fact in the configuration table. Once a cap exists, record it, stop a harness when its measured spend reaches the cap, and report spend per run.

## Records

Capture these per run in the result note:

1. Full configuration (table above), including date and harness version.
2. Exact input: the scratch suite hash (`sha256sum`) before the writer, after the writer, after the seeding, and after the resumer.
3. Prompt text and role block as run, if different from the template.
4. Outputs: final suite diff (the new cases only), checker output summary (`correct`, `total`, `passed`), and the handoff note text.
5. Failures and stop reason for each phase.
6. Correction log: time, category, one-line description.
7. Latency and trajectory numbers from "Measures".
8. Reproducibility: repeat count and agreement.

## Decision rule

Answer "what is the smallest useful option" using the cheapest configuration that meets all of these:

- Final suite passes the checker in at least 2 of 3 repeats.
- Seeded defect is `detected and fixed` or `detected and reported` in at least 2 of 3 repeats.
- No boundary violations.
- Human corrections at most 2 per full writer and resumer pair, none in the `boundary` category.

Order by: fewer corrections, then lower handoff latency, then lower cost. Report the smallest option that passes, then whether a heavier option measurably beat it on a dimension that matters.

- **Adopt** an alternative only if it passes while the baseline fails, or it passes with clearly lower correction count or latency across at least 3 repeats.
- **Reject** an alternative that fails any gate, needs paid access without a cap, or lacks a required capability.
- **No meaningful difference** (stop condition): if all configurations that run pass the gates and differ by less than one correction and 20% latency, record the baseline as the smallest useful option and stop.

Adoption here means "worth a further, larger experiment", not a rollout. Production use, authority grants, and deployment are out of scope.

## Threats to validity

- Small sample and one task. Treat results as operational lessons, not rankings.
- A model that has seen this public repository or its policy may recall the answer; the facilitator should note any sign of this.
- The facilitator knows the seeded defect and may bias corrections; log every intervention and keep wording neutral.
- Harness versions change quickly; results apply only to the recorded versions and date.
- Differences in instruction-file discovery are part of the configuration under test, not noise.
