# Observability: an open-source, AI-native, unified stack

Status: proposal for review, prepared 2026-10-10. Nothing is built, and no issue, board item or other pull request is changed by this document. The change plan in section 8 is applied only after approval.

Evidence: four parallel reviews (ingestion, storage, visualization, AI analysis) checked sources on 2026-10-10. Their notes, with every citation, are in [observability/](observability/). In this document **FACT** means a reviewer read it at the cited source; **INFERENCE** means judgement. Each claim below links to the review that carries its source.

## 1. Decision summary

| Area | Recommendation now | Grow into | Main reason |
| --- | --- | --- | --- |
| Ingestion | OTLP as the only wire format; one OpenTelemetry Collector on localhost doing redaction and buffering | Agent and gateway Collector tiers; OpAMP only for a multi-host product | Every emitter that matters already speaks OTLP, and the Collector is the one place to enforce redaction ([ingestion](observability/ingestion.md)) |
| Storage | The existing Postgres: a `telemetry` schema with its own role, daily partitions, OTel-shaped columns | ClickHouse single node when a measured trigger fires; Parquet/DuckLake for cold data | ADR 002 (no new infrastructure without a workload), one backup target, SQL joins with `runs` and pgvector ([storage](observability/storage.md)) |
| Visualization | Grafana OSS, unmodified, with its built-in Postgres datasource; dashboards as JSON in Git | Grafana or HyperDX for infrastructure, Langfuse for agent traces and evals, a thin Chimken UI embedding Perses for a product | Lightest option that reads Postgres directly; every LLM-specific UI except Phoenix needs ClickHouse ([visualization](observability/visualization.md)) |
| AI analysis | A small Chimken MCP server with named read-only queries; deterministic detection first; an LLM only explains and proposes; hosted models only behind a tested redaction gate | Drain3 templates, pgvector error signatures, eval judges, a scorecard that feeds the #51 router | Telemetry is untrusted input to a model, and SQL over a curated schema is what models query best ([ai](observability/ai.md)) |

The product seam, if Chimken observability becomes its own product, is not the database or the dashboards. It is three owned contracts: the OTLP-to-schema mapping for agent runs, the read-only analysis interface (MCP), and the layered authority model in section 5. Storage and UIs sit behind those contracts and stay swappable (INFERENCE).

## 2. Constraints this design honours

- The repository is permanently public. Telemetry can hold prompts, tool output and household data, so it lives only in the data layer (ADR 004 in PR #47). Collector configs, schemas, dashboards and redaction fixtures are public; telemetry rows are not.
- Postgres is the agreed default, with pgvector for RAG, and agent run logs are planned as a Postgres `runs` table (draft ADR 007, proposed and not yet in the repository). This design adds a `telemetry` schema beside it rather than a second database.
- ADR 002: add infrastructure only when a workload proves need. Every scale-out step below has a measured trigger.
- ADR 003: a model never grants its own authority, and retrieved text is data, not instructions. Section 5 applies this to telemetry analysis.
- Open source for a possible product: AGPL stores, ELv2 and the Timescale License are avoided in anything a product might host.

Where it departs from the Postgres default: once host logs and metrics or a high-volume workload arrive, Postgres stops being the right telemetry store and ClickHouse takes over (section 3.2). `runs`, evals and embeddings stay in Postgres even then.

## 3. Options and trade-offs per area

### 3.1 Data ingestion

| Option | Verdict | Why |
| --- | --- | --- |
| **OpenTelemetry Collector** (custom `ocb` build from contrib) | **Choose** | Apache-2.0 and CNCF. It has a `redaction` processor (allowlist, regex masking, HMAC hashing), a disk-backed persistent queue, and tail sampling. Still 0.x with releases about every two weeks (v0.162.0 on 2026-09-29). FACT. |
| Grafana Alloy | Only if the backend becomes Grafana's LGTM stack | An OTel Collector distribution with its own config syntax. FACT. That syntax is a lock-in surface (INFERENCE). |
| Vector | Skip | MPL-2.0, owned by Datadog, pre-1.0 (0.59.0), and its OTLP sink began logs-only. FACT. |
| Fluent Bit | Skip unless heavy host log tailing appears | Very small but logs-first; weak for traces (INFERENCE). Try the Collector's `filelog` and `journald` receivers first. |

What the agents emit (FACT, [ingestion](observability/ingestion.md) section 2):

- **Claude Code** sends OTLP metrics and log events once `CLAUDE_CODE_ENABLE_TELEMETRY=1` is set. Traces are beta behind `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`. Prompts are redacted by default, and tool content is off unless opted in.
- **Codex CLI** has an `[otel]` section, off by default. Its `tool_result` event carries an output snippet even with prompt logging off, so the Collector must drop or truncate it.
- **Neither uses the `gen_ai.*` names.** The OTel GenAI conventions are still at Development stability and moved to their own repository in June 2026 with no tagged release. Chimken therefore stores raw attributes as JSONB and keeps a versioned mapping, rather than hard-coding `gen_ai.*` columns.
- **Python libraries.** Prefer the official OTel GenAI instrumentations, and OpenInference (Apache-2.0) where they don't reach, such as the Claude Agent SDK. ServiceNow announced it is buying Traceloop, which makes OpenLLMetry's future uncertain. Watch out: the PyPI name `opentelemetry-instrumentation-anthropic` belongs to Traceloop, not to OpenTelemetry.
- **Not checked:** Gemini CLI and Grok telemetry.

### 3.2 Storage

| Option | License (FACT) | Fit now | Fit at product scale | Verdict |
| --- | --- | --- | --- | --- |
| **Postgres, same instance**, native partitioning (pg_partman later if needed) | PostgreSQL | Best: zero new services, joins with `runs`, one backup | Poor beyond about 1-5 GB/day (INFERENCE) | **Now** |
| **ClickHouse** single node + OTel exporter | Apache-2.0 | Too heavy: 4 GB RAM minimum, 8 GB+ in practice | Built for it; ClickStack, SigNoz, Langfuse all run on it | **Next, on a trigger** |
| GreptimeDB | Apache-2.0, 1.0 GA 2026-04-14 | Plausible single binary, SQL plus PromQL | Promising, but young | Runner-up |
| VictoriaMetrics / Logs / Traces | Apache-2.0 | Very light | Good | No SQL; VictoriaTraces still 0.x |
| Loki / Mimir / Tempo (LGTM) | AGPL-3.0 | Three services, three query languages | Proven | Avoid for product use; no cross-signal joins |
| TimescaleDB | Core Apache; telemetry features under the Timescale License | Fine for self-use | Bans offering those features as a service | Avoid as a foundation |
| OpenObserve | AGPL-3.0, relicensed from Apache in Nov 2023 | Light | Relicense history | Avoid |
| Quickwit | Apache-2.0, team moved to Datadog | n/a | Abandonment risk (INFERENCE) | Avoid |
| Parquet + DuckLake (1.0, Postgres catalog) | MIT / Apache-2.0 | Cold tier only | Cold tier | Archive tier later |

Why SQL matters for being AI-native (INFERENCE): models write SQL far more reliably than LogQL, TraceQL or MetricsQL, a SQL store lets one query join spans with `runs` and pgvector, and SQL stores have mechanical guardrails (read-only roles, `statement_timeout`, `EXPLAIN`). This is the strongest argument against the LGTM stack for this brief.

**Move telemetry out of the app Postgres when any of these is measured** (thresholds are INFERENCE and should be tuned once real data exists):

1. Sustained ingest above about 1 GB/day, or about 50M rows a month.
2. Telemetry writes or vacuum measurably slow the app, or telemetry exceeds 70% of backup size.
3. Host or container logs and metrics are needed, not just agent run spans.
4. A ready-made trace UI is needed that would be costly to rebuild.
5. The product track starts.

A cheaper intermediate step is a second database on the same Postgres cluster, or pg_duckdb with Parquet for the cold tier.

### 3.3 Visualization

| Option | License (FACT) | Needs | Verdict |
| --- | --- | --- | --- |
| **Grafana OSS** | AGPLv3 core, Apache-2.0 plugins; running unmodified is unaffected | One binary, built-in Postgres datasource | **Now**, as the infrastructure and run-metrics UI |
| Jaeger v2 | Apache-2.0, CNCF graduated | One binary with Badger storage | Optional span-tree viewer before ClickHouse |
| **Langfuse** | MIT core (`ee/` excluded); LLM-as-judge and annotation queues are MIT; ClickHouse bought it 2026-01-16; v4 GA 2026-08-17 | Postgres + ClickHouse + Redis + S3 | **Later**, as the agent-trace and eval UI |
| HyperDX / ClickStack | MIT; ClickHouse bought it 2025-03-13 | ClickHouse + MongoDB | Infrastructure UI alternative once ClickHouse lands |
| SigNoz | MIT except `ee/` | ClickHouse + Keeper | Closest to one UI for both, but no evals and a fixed AI dashboard |
| Perses | Apache-2.0, CNCF Sandbox, embeddable npm panels | One binary; no Postgres plugin | Building block for a product UI |
| Opik | Apache-2.0 | ClickHouse + MySQL + Redis + MinIO | Fallback if Langfuse closes features |
| Arize Phoenix | **ELv2**, not open source | One container | Exclude: forbids hosted use |
| Helicone | Apache-2.0, maintenance mode after Mintlify bought it | Several stores | Exclude |
| Metabase / Superset | AGPL / Apache-2.0 | JVM / Python + Redis | Superset only if non-engineers need ad-hoc BI |

No single self-hosted UI covers infrastructure and agent telemetry well (INFERENCE). The workable pattern is two surfaces over one data plane, linked by the OTel `trace_id` stored on each `runs` row. Grafana's own AI observability views (tokens, cost, online evals) are documented only for Grafana Cloud (FACT), so they don't count here.

### 3.4 AI integrations

Telemetry is untrusted input to a model. Log lines, tool output and transcripts carry text written by web pages, emails and people, so an analysis model gets no write tools and no egress (OWASP LLM01, FACT; ADR 003). Read-only must be enforced by the database role, not by an MCP wrapper. Datadog found SQL injection in Anthropic's reference Postgres MCP server that bypassed its read-only mode (FACT, [ai](observability/ai.md) 1.4).

| Option | Status (FACT) | Verdict |
| --- | --- | --- |
| **Own Chimken MCP server** (FastMCP) over curated views | n/a | **Now.** Named, parameterised queries; read-only role; row caps; audit log. Doubles as the product's AI surface. |
| grafana/mcp-grafana | Apache-2.0; has write tools | Later, with `--disable-write` and a Viewer token |
| ClickHouse/mcp-clickhouse | Apache-2.0, v0.4.0, read-only by default | With ClickHouse, behind a read-only user |
| Postgres MCP Pro | MIT; its README says its restricted mode can be bypassed | Skip in favour of the own server |
| SigNoz MCP | About 40 tools, no read-only mode documented | Only with SigNoz, behind a viewer key |
| HolmesGPT | CNCF Sandbox, Apache-2.0, any OpenAI-compatible model | Optional later, read-only with remediation off; Kubernetes-centric |
| Grafana Assistant / Sift | Self-managed installs must link a Grafana Cloud account | Exclude: not open source, sends data out |
| DeepEval, Inspect AI | Apache-2.0, MIT | Eval judges as libraries writing to an `evals` table |

Detection stays deterministic: alert rules, SQL z-score views and Drain3 log templates first; Isolation Forest or Prophet only if they earn it. Household volume is too small for ML detection to beat thresholds (INFERENCE). Embeddings go on normalised error signatures, computed by a local model, not on raw logs, so pgvector does not become a second copy of sensitive text.

**Hosted models on redacted data only (decided 2026-10-10).** Hosted models (Claude, Codex, Gemini, Grok) may triage telemetry, but only through a redaction gate, and the gate is a tested component, not a convention:

- **One egress path.** Only the Chimken MCP server assembles context for a hosted call. It reads curated views through the read-only role, runs the bundle through a redaction step (field allowlist first, then pattern and entity masking such as Presidio, then HMAC tokens for identifiers so rows still join), and refuses to send anything that fails it.
- **Fail closed.** A bundle with a field outside the allowlist, a redaction error, or a detector hit after masking is not sent. The finding is still summarised by a local model or left for a person.
- **Tested in CI.** A fixture suite of synthetic PII (names, addresses, emails, phone numbers, account numbers, health and finance phrases, secrets, Codex `tool_result` snippets) must come out fully masked; any leak fails the build. The suite grows with every miss found in review.
- **Logged.** Every hosted call records the bundle hash, the redaction version, the model and the finding it served, so what left the house can be audited.
- **Why an allowlist and not detection alone.** Presidio states it cannot guarantee it finds everything (FACT, [ai](observability/ai.md) section 9), so detection is the second line, not the first.
- Raw content events (prompts, tool output) never go to a hosted model, redacted or not. Aggregates, error templates and redacted span fields do.

## 4. Target architecture

```text
 Claude Code ─┐  OTLP (content off at source)
 Codex CLI ───┤
 Gemini, Grok ┤ (to verify)
 Chimken code ┘  OTel SDK, root span per run with run.id
        │
        ▼
 OTel Collector (localhost): memory_limiter → redaction allowlist → transform
        │                     (drop content, truncate Codex snippets) → batch
        │                     persistent file queue
        ▼
 ┌────────────── data layer, never Git ─────────────────────────┐
 │ Postgres: runs, evals, findings  │  telemetry.spans/events   │
 │           pgvector error sigs     │  (daily partitions)       │
 │  ── later, on a trigger ──  ClickHouse otel_* tables + TTL   │
 │                              Parquet/DuckLake cold archive    │
 └───────────────────────────────────────────────────────────────┘
        │ read-only roles
        ├── Grafana OSS (Postgres, later ClickHouse datasource)
        ├── Langfuse (later; shares ClickHouse)
        └── Chimken MCP server ──► L2 deterministic checks ──► findings
                                   L3 model proposals (hosted only via redaction gate)
                                   L4 policy + human approval
```

## 5. Authority layers for AI analysis

| Layer | Does | Authority |
| --- | --- | --- |
| L0 Data | SQL-friendly schema with documented columns and curated views (`v_run_summary`, `v_daily_cost`, `v_failures`) | n/a |
| L1 Access | Chimken MCP server: `describe_view`, `query_view(name, filters, limit≤200)`; later a guarded `sql_select` and `similar_errors(k)` | Read-only database role, `statement_timeout`, row caps, every call logged |
| L2 Deterministic | Alert rules, z-scores, Drain3 templates | May open a `findings` row |
| L3 Model | Explains, summarises, judges. Hosted models only on bundles that passed the redaction gate (section 3.4); local models for embeddings and for anything the gate rejects | Writes proposals only; no tools beyond the read-only MCP server |
| L4 Action | Allowlisted, reversible actions such as pausing an agent or lowering a routing weight | Deterministic policy plus human approval; a model never triggers it |

The feedback loop into #51: runs and evals produce a scorecard per task kind, agent and model, and the router reads only those aggregates. A model cannot raise its own share except through measured outcomes, and anything that widens authority needs a person (INFERENCE, consistent with ADR 003).

## 6. Phased rollout

Each phase ships on its own and is only started when the previous exit criteria hold.

| Phase | Scope | Exit criteria |
| --- | --- | --- |
| **0. Contract** (no running infrastructure) | ADR for observability; schema for `telemetry.spans`, `telemetry.events`, `findings`, `evals` beside `runs`; Collector config with redaction rules; synthetic PII fixtures | A CI test pushes fake PII through the Collector config and asserts it is removed; ADR accepted |
| **1. See agent runs** | Postgres `telemetry` schema with daily partitions and retention by partition drop; localhost Collector; Claude Code and Codex pointed at it with content off; OTel SDK root span per run; small OTLP-to-Postgres writer; Grafana OSS with provisioned dashboards (runs by agent, outcome, duration, tokens, cost) | Two weeks of real runs from at least two harnesses visible; no fixture leak; the restore drill (#33) and backups (#50) cover the schema; collector restart loses no data |
| **2. Read-only AI triage** | Chimken MCP server with named queries and the redaction gate; deterministic checks (failure rate, cost z-score > 3) writing `findings`; a triage task that summarises each finding with no write tools, using a hosted model only on gated bundles | The redaction fixture suite passes with zero leaks and the gate fails closed on a malformed bundle; every hosted call is logged with bundle hash and redaction version; every finding gets a summary; human accept rate is recorded; an instruction planted in a synthetic log line does not change the agent's tool use |
| **3. Evals and learning** | DeepEval or Inspect judges writing `evals`; a small human-labelled calibration set; Drain3 templates; pgvector error signatures with local embeddings; scorecard view consumed by the #51 router as rules | Judge-to-human agreement measured and above an agreed bar; "seen this before" returns a useful match on real repeat failures; routing decisions are recorded with the scorecard they used |
| **4. Scale out** (only on a section 3.2 trigger) | ClickHouse single node with TTL and its own backup; Collector exports there; Langfuse on the same ClickHouse; host logs and metrics via `filelog`/`journald`; tail sampling at a gateway Collector; Parquet/DuckLake cold tier | A copy job moves history with matching row counts and hashes; dual-write parity for a week; Grafana and Langfuse both link by `trace_id`; backup and restore drill include ClickHouse |
| **5. Product** (only after a product decision) | Versioned telemetry contract and storage adapters; multi-tenant isolation; OpAMP fleet management; thin Chimken UI embedding Perses and linking to Langfuse and Grafana | A second, isolated tenant runs end to end on the published contract; no AGPL, ELv2 or Timescale License component in the hosted path |

## 7. What would change the verdict

| If this happens | Then |
| --- | --- |
| Measured volume is ten times the estimate from the start | Skip phase 1's Postgres store and go straight to ClickHouse + HyperDX + Langfuse |
| The product will never be hosted for others | AGPL stops mattering; LGTM and Grafana patches become acceptable |
| ClickHouse, HyperDX or Langfuse relicense or move core features to paid tiers | Switch to GreptimeDB or Victoria for storage and Opik for agent traces |
| OTel GenAI conventions reach Stable, or Claude Code and Codex emit `gen_ai.*` | Map straight into typed columns instead of JSONB plus mapping |
| A redaction leak reaches a hosted model, or the fixture suite cannot keep up with real data | Stop hosted triage and fall back to local models until the gate is fixed |
| Grafana ships a fully local, open-source Assistant | Re-evaluate it against the own MCP server |
| Chimken moves to Kubernetes | HolmesGPT becomes worth adding, read-only |

## 8. Annotated change plan (applied only after a yes)

| # | Change | Why |
| --- | --- | --- |
| 1 | Merge this document and its four review notes | Records the analysis and its sources where every harness reads |
| 2 | Add `docs/adr/008-observability-stack.md` (proposed) covering OTLP-only ingestion, telemetry in Postgres first, the move triggers, and the authority layers | Makes the decision reviewable; 008 because 004 to 007 are taken or proposed |
| 3 | `docs/architecture.md`, Infrastructure row: link this document | Hand to the PR #47 owner rather than editing it here |
| 4 | New issues, one per phase 0 to 3, under the observability epic #58, after the gated review in #60 passes, each with the exit criteria above; phases 4 and 5 as a single parked issue listing the triggers | Makes the work trackable without committing to scale-out |
| 5 | Link #50 and #33 so the `telemetry` schema is in backups and the restore drill | Telemetry not restored is telemetry lost |
| 6 | Link the phase 3 issue to #51 | The router consumes the scorecard |

## 9. Decisions and open points

- Decided 2026-10-10: start on Postgres (phases 0 and 1); ClickHouse comes later as a copy job when a section 3.2 trigger fires.
- Decided 2026-10-10: hosted models may triage telemetry only after it passes the tested redaction gate in section 3.4. The read-only and no-autonomous-action rules stand.

## 10. Known gaps

- GitHub API access was blocked for the reviewers, so recent commit activity for Quickwit, SigNoz's `ee/` scope, and Drain3's license were not confirmed.
- No maintained OTel Collector exporter for Postgres was confirmed, so phase 1 assumes a small in-repo writer.
- Gemini CLI and Grok telemetry support was not checked.
- Resource and compression figures are typical published values, not benchmarks run here.
