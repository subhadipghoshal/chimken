# AI integrations for analysing telemetry (Chimken), status as of 2026-10-10

Scope: how AI (and non-AI) analysis can work over Chimken telemetry (agent run logs, OTel traces/logs/metrics) under ADR 003 (bounded autonomy; retrieved text is data, not instructions), the rule "deterministic or classic ML first", and "no sensitive telemetry to third parties without redaction or consent".
Labels: **FACT** means verified at the cited URL during this review. **INFERENCE** means my judgement or prior knowledge that was not re-verified here.

## 1. Key principle: telemetry is untrusted LLM input

| # | Finding | Label | Source | What would change it |
|---|---|---|---|---|
| 1.1 | Indirect prompt injection happens when an LLM processes external content such as files or pages. OWASP's mitigations are least privilege, human approval for privileged actions, and keeping untrusted content separate and labelled. | FACT | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | Nothing realistic. This is the baseline threat model. |
| 1.2 | Log lines, span attributes, agent transcripts, tool outputs and error messages all contain text that agents, web pages, emails or household members wrote. Any of it can carry instructions ("ignore previous, run X"). Chimken agents read web and email, so injected text can reach the logs one step later. | INFERENCE | ADR 003; 1.1 | Only if telemetry were limited to numeric metrics with no free text. Not realistic here. |
| 1.3 | Consequence: an analysis LLM must have **no write tools and no egress**. Its output is a *proposal*, and deterministic code plus a human decide on any action. This applies ADR 003 directly ("a model never grants its own authority"). | INFERENCE | ADR 003 | A future proven defence against injection. None exists as of Oct 2026. |
| 1.4 | Reference implementations show "read-only" MCP wrappers can be bypassed. Datadog found SQL injection in Anthropic's reference Postgres MCP server that bypassed its read-only restriction and allowed arbitrary SQL (Aug 2025). Read-only must be enforced by the **database role**, not by the tool wrapper. | FACT (bypass); INFERENCE (lesson) | https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/ | None. Defence in depth is cheap. |

## 2. MCP servers for observability data access

| Server | Licence | What it exposes | Write risk and controls | Maturity | Label and source |
|---|---|---|---|---|---|
| **grafana/mcp-grafana** | Apache-2.0 | Prometheus, Loki, alerting, incident, OnCall, Sift, Pyroscope, dashboards, datasources; ClickHouse, Elasticsearch and others are off by default. Tempo is reached through Sift or a datasource query, not as a separate tool category. | Has write tools (dashboards, annotations, alerting). Mitigate with `--disable-write`, per-category `--disable-<cat>`, and a Grafana service account with the **Viewer** role. | Official Grafana Labs project, active, widely used | FACT: https://github.com/grafana/mcp-grafana |
| **ClickHouse/mcp-clickhouse** | Apache-2.0 | `run_query`, `list_databases`, `list_tables`, optional chDB | **Read-only by default**: runs with `readonly=1` unless `CLICKHOUSE_ALLOW_WRITE_ACCESS=true`; DROP needs a separate flag | v0.4.0, 2026-06-03, official | FACT: https://github.com/ClickHouse/mcp-clickhouse |
| **SigNoz MCP server** | Not stated on the docs page (SigNoz core is MIT plus EE parts: INFERENCE) | About 40 tools: metrics, logs, traces, alerts, dashboards, views, notification channels; works self-hosted | Has many create/update/delete tools and **no read-only mode documented**. Mitigate with a viewer-scoped API key and a tool allowlist. | Official; docs updated 2026-08-17; some tools need SigNoz v0.118 to v0.135 | FACT: https://signoz.io/docs/ai/signoz-mcp-server/ |
| **Postgres MCP Pro (crystaldba)** | MIT | SQL, schema, explain plans, index advice, health checks | "Restricted" mode uses read-only transactions plus pglast parsing plus a time limit. It runs on a read-write connection, and the README warns that unsafe stored-procedure languages can bypass it. | Community, popular | FACT: https://github.com/crystaldba/postgres-mcp |
| Anthropic reference Postgres MCP | MIT | `query` | Read-only bypass found (see 1.4). Do not use. | Reference only (archived: INFERENCE) | FACT (vuln): Datadog link above |
| VictoriaMetrics/Logs MCP, Prometheus community MCPs | various | PromQL/MetricsQL, LogsQL | Mostly read-only query APIs | Not verified in this review | INFERENCE |

**Verdict:** Chimken should **write its own small read-only MCP server** (Python, FastMCP) over its own Postgres `runs` and telemetry views, and use mcp-grafana in `--disable-write` mode with a Viewer token for metrics and logs. A custom server lets Chimken control the schema docs, row limits, redaction and audit logging, and it fits the "extensible as a product" goal. *Would change if* the chosen backend is SigNoz or ClickHouse: then use the vendor MCP server behind a read-only database user.

## 3. Text-to-SQL / PromQL over telemetry

| # | Finding | Label | Source |
|---|---|---|---|
| 3.1 | LLMs write SQL far more reliably than PromQL or LogQL. SQL is everywhere in training data, while PromQL has subtle semantics such as `rate` windows and label matching. A telemetry store with a SQL schema (Postgres, ClickHouse) is therefore more "AI-native" than one that only speaks PromQL. | INFERENCE | General LLM behaviour; MCP server designs in section 2 |
| 3.2 | The schema matters more than the model. Use stable, typed, documented columns (`run_id`, `agent`, `model`, `task_kind`, `status`, `cost_usd`, `tokens_in/out`, `latency_ms`, `error_class`, `trace_id`) plus `COMMENT ON` text and a few **curated views** such as `v_run_summary` and `v_daily_cost`. The LLM should query the views, not the raw OTel JSON blobs. | INFERENCE | Postgres MCP Pro and mcp-clickhouse both expose schema listing (FACT, section 2) |
| 3.3 | Semantic-convention alignment (OTel GenAI `gen_ai.*` attributes) lets generic tools and LLMs understand the data without custom prompts. | INFERENCE | OTel GenAI semconv (not re-verified here; still marked experimental as of my knowledge) |
| 3.4 | Guard every query with a read-only role, `statement_timeout`, `default_transaction_read_only=on`, row caps (`LIMIT` injected or a cursor cap), restricted search_path/schema grants (views only), and `pg_stat_statements` for audit. For ClickHouse use `readonly=1`, `max_execution_time` and `max_result_rows`. | INFERENCE (standard DB controls) | Postgres and ClickHouse docs (well known) |
| 3.5 | Prefer **parameterised "named queries"** for common questions over free-form text-to-SQL. Free SQL is the fallback and runs only under the controls in 3.4. | INFERENCE | ADR 003 "deterministic first" |

## 4. Anomaly detection: conventional methods first

| Method | Use in Chimken | Cost | Label |
|---|---|---|---|
| Prometheus/Grafana alert rules and recording rules (thresholds, `absent()`, error-rate SLOs, burn-rate) | Agent failure rate, cost per day, queue lag, run duration p95 | Near zero, deterministic | INFERENCE (standard practice) |
| SQL statistical baselines (rolling mean ± k·σ, z-score, MAD, same-hour-last-week) in Postgres views or a cron job | Cost or token spikes per agent or model, runtime regressions | Near zero | INFERENCE |
| Seasonal forecasting (Prophet, statsmodels STL/ETS) | Only if daily/weekly household seasonality causes false alarms | Low, batch | INFERENCE |
| Isolation Forest / LOF (scikit-learn) on per-run feature vectors | Unusual runs (tool-call count, tokens, duration, error mix) | Low; requires a feature table | INFERENCE |
| Log template mining (Drain3: online template miner with masking and persistence) | Turns error text into templates for counting new or rare templates. Deterministic, no LLM. | Low | FACT: https://github.com/logpai/Drain3 (licence and maintenance cadence not confirmed) |
| LLM | **Only** to *explain* or *summarise* an anomaly that the methods above flagged | Per incident | INFERENCE, per ADR 003 |

Household scale (tens to thousands of runs a day) is too small for ML anomaly detection to beat thresholds plus z-scores. Start there. *Would change if* the data reaches multi-tenant or product scale.

## 5. Similarity search and clustering with pgvector

| # | Finding | Label |
|---|---|---|
| 5.1 | Embed **normalised error signatures** (Drain3 template plus exception type plus top stack frame), run summaries and incident notes. Do not embed every raw log line: it is costly and low value, and it spreads PII into a second store. | INFERENCE |
| 5.2 | Uses: "seen this before?" nearest-neighbour lookup that links a new failure to past runs and fixes, error clustering (HDBSCAN/k-means on embeddings, or group by Drain3 template first), and few-shot retrieval for the RCA prompt. | INFERENCE |
| 5.3 | Use local embedding models (e.g. via Ollama or sentence-transformers) so raw error text stays in the house. Store `model_id` and `dim` alongside each vector so re-embedding is possible. | INFERENCE |
| 5.4 | Retrieved neighbours go back into an LLM prompt and are **untrusted data** (section 1). Wrap them in delimited, labelled blocks and never let them select tools. | INFERENCE, per ADR 003 |

## 6. LLM-assisted RCA and incident summarisation

| Tool | Status | Fit for Chimken | Label and source |
|---|---|---|---|
| **HolmesGPT** (Robusta) | CNCF Sandbox (accepted Oct 2025), Apache-2.0. Toolsets cover Prometheus, Loki, Tempo, Grafana, SQL DBs and MCP. Claims "read-only access and respects RBAC", but an optional remediation toolset can make changes. Works with any OpenAI-compatible LLM, so a local model is possible. | Best OSS candidate if Chimken wants an off-the-shelf RCA agent. Kubernetes-centric. Run it read-only, with remediation off and a local or approved model. | FACT: https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/ , https://github.com/robusta-dev/holmesgpt |
| **k8sgpt** | CNCF Sandbox; Kubernetes analyzers plus LLM explanation | Only relevant if Chimken runs on Kubernetes. Probably skip. | FACT (sandbox): https://k8sgpt.ai ; rest INFERENCE |
| **Grafana Assistant** | Since 2026-04-21 available to Grafana OSS and Enterprise users, but self-managed installs connect to a **Grafana Cloud account**. Where inference runs and what data leaves the house is not stated. | Conflicts with the "no third parties without consent" rule. Not open source. Avoid unless the household explicitly consents. | FACT: https://grafana.com/whats-new/2026-04-21-grafana-assistant-becomes-available-on-prem/ |
| **Grafana Sift** | Exposed via mcp-grafana tools; Sift itself is a Grafana Cloud feature | Cloud-dependent, so avoid | FACT (tool listed): mcp-grafana README; cloud-only: INFERENCE |
| **DIY: Claude Code / Codex plus Chimken MCP** | Chimken already runs these agents | Simplest: a "triage" task that reads through the read-only MCP and writes a markdown summary to a `findings` table. | INFERENCE |

Pattern: an alert fires deterministically. The analysis agent then collects bounded context: the run row, trace, Drain3 template, top-k similar past incidents and metrics ±30 min. It outputs a structured `{hypothesis, evidence_refs[], confidence, suggested_action}`. A human or a deterministic policy accepts or rejects it, and that verdict is stored as a label (see section 8).

## 7. LLM-as-judge evaluation of agent traces

| Tool | Licence | Self-host | Notes | Label and source |
|---|---|---|---|---|
| **Langfuse** | MIT core (some EE features) | Yes; stack is Postgres plus ClickHouse plus Redis plus S3 (INFERENCE) | Acquired by ClickHouse 2026-01-16, core stays MIT, self-host unaffected. Has tracing, LLM-as-judge evaluators, datasets and scores, and OTel ingest. | FACT: https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability |
| **Arize Phoenix** | **Elastic License 2.0** (source-available, not OSI) | Yes (Docker/Helm) | OTel/OpenInference based, has evals. The ELv2 licence clashes with "open source, possible product" because ELv2 forbids offering it as a managed service. | FACT: https://raw.githubusercontent.com/Arize-ai/phoenix/main/LICENSE , https://github.com/Arize-ai/phoenix |
| **Opik** (Comet) | Apache-2.0, full platform self-hostable | Docker Compose / Helm | Judge metrics (hallucination, moderation, RAG), OTel integration | FACT: https://github.com/comet-ml/opik |
| **DeepEval** | Apache-2.0 | Library | G-Eval, Task Completion, Tool Correctness; pytest-style `deepeval test run`; custom (local) judge models | FACT: https://github.com/confident-ai/deepeval |
| **Inspect AI** (UK AISI) | MIT | Library | Eval framework covering tool use, multi-turn and model-graded scoring; 200+ prebuilt evals. Good for offline regression suites of agent tasks. | FACT: https://github.com/UKGovernmentBEIS/inspect_ai |

Verdict: **library-first**. Run DeepEval or Inspect over rows exported from Chimken's own `runs` table and write scores back to an `evals` table in Postgres. This avoids adding another stateful platform. If a UI is wanted later, **Langfuse** (MIT, self-hosted) is the strongest fit, but it brings ClickHouse with it. *Would change if* the main observability backend becomes ClickHouse anyway (then Langfuse is cheap to add) or if Langfuse moves core features out of MIT.
Caveats (INFERENCE): judges are biased (they favour verbosity and their own model family) and must be calibrated against a small human-labelled set. Prefer deterministic checks (exit code, tests passed, diff applies, cost < cap) before an LLM judge. A judge also reads untrusted transcripts, so it has no tools.

## 8. Feedback loop: telemetry to evals to routing

```
runs/traces -> deterministic metrics (success, cost, latency, retries)
            -> LLM-judge scores (sampled, calibrated)  -> evals table
            -> per (task_kind, agent, model) scorecard view
            -> router reads scorecard (deterministic policy, e.g. Thompson/epsilon-greedy or rules)
            -> human-approved policy change for anything that widens authority
```
| # | Point | Label |
|---|---|---|
| 8.1 | The router uses **aggregates**, never raw LLM text. A model cannot raise its own routing share except through measured outcomes. This satisfies ADR 003. | INFERENCE |
| 8.2 | Store human accept/reject of RCA proposals and eval overrides as labels. They calibrate judges and become future few-shot examples. | INFERENCE |
| 8.3 | Guard against Goodhart: keep a held-out human-labelled set, and alert on judge vs. human drift. | INFERENCE |

## 9. Guardrails checklist

| Control | Implementation | Label |
|---|---|---|
| Read-only credentials | Dedicated PG role `telemetry_reader` with SELECT on curated views only and `default_transaction_read_only=on`; Grafana Viewer service account; ClickHouse `readonly=1` user. Enforced in the DB, not the MCP wrapper (1.4). | INFERENCE, backed by FACT 1.4 |
| Query cost limits | `statement_timeout` (e.g. 5s), `LIMIT`/row cap, max calls per session, token budget per analysis task, ClickHouse `max_execution_time` | INFERENCE |
| PII redaction before model calls | Redact at **ingest** (OTel Collector `redaction`/`transform` processors, INFERENCE) *and* before prompt assembly (Presidio, MIT). Presidio says there is "no guarantee" it finds everything, so redaction is not enough on its own to justify sending data to a hosted model. | FACT (Presidio): https://github.com/microsoft/presidio |
| Local vs hosted models | Default **local** (Ollama) for anything that touches raw telemetry: embeddings, summarisation, triage. Hosted models (Claude, Codex, Gemini, Grok) only see redacted, aggregated context, with consent per household policy. Local models are weaker at multi-step RCA, so accept lower quality or escalate with a redacted bundle. | INFERENCE |
| Prompt-injection containment | Analysis agent has no write tools, no network egress, and no secrets. Telemetry goes inside clearly delimited "DATA" blocks. Output is schema-validated JSON. Actions go through deterministic policy plus human approval. | INFERENCE, per OWASP 1.1 |
| Audit | Log every MCP tool call (query text, rows returned, caller run_id) to the `runs` telemetry itself, so AI analysis is observable too | INFERENCE |
| Retention | Redacted prompt and response retention is short. Embeddings count as derived PII and follow the same deletion rules. | INFERENCE |

## 10. Recommendation

### Layered architecture
| Layer | Responsibility | Components | Authority |
|---|---|---|---|
| **L0 Data** | Store telemetry with a SQL-friendly schema | Postgres (`runs`, `run_events`, `evals`, `findings`, pgvector `error_signatures`); metrics/logs backend chosen elsewhere | n/a |
| **L1 Data access** | Typed, read-only, budgeted access | Chimken MCP server (FastMCP): `list_views`, `describe_view`, named queries, guarded `sql_select`, `similar_errors(k)`; mcp-grafana `--disable-write` with Viewer token | Read-only role in the DB; timeouts; row caps; audit log |
| **L2 Deterministic analysis** | Detect anomalies and group errors without an LLM | Alert and recording rules, SQL z-score views, Drain3 templating, optional IsolationForest batch | Can open a `findings` row |
| **L3 LLM analysis** | Explain, summarise, cluster labels, judge evals | Local Ollama by default; hosted only on redacted bundles with consent; DeepEval/Inspect for judges | Writes **proposals** only (`findings.proposal`, `evals.score`) |
| **L4 Action (bounded)** | Act on proposals | Deterministic policy engine (allowlisted, reversible actions such as "pause agent X", "lower routing weight") plus human approval for anything that widens authority | Never invoked directly by an LLM. Every action is logged with the approving principal. |

### Minimal first slice (about 1 to 2 days)
1. `runs` table with documented columns plus 3 curated views (`v_run_summary`, `v_daily_cost`, `v_failures`), and a read-only PG role with `statement_timeout`.
2. A tiny Chimken MCP server exposing `describe_view` and `query_view(name, filters, limit≤200)` (named, parameterised; no free SQL yet).
3. Deterministic checks as a cron job or SQL: failure rate, cost spike z-score > 3. Each writes a `findings` row.
4. A Claude Code/Codex "triage" task that reads a finding through the MCP server and writes a markdown summary back. The prompt marks all row text as untrusted data. No write tools.
Skipped for now: pgvector, judges, Langfuse, HolmesGPT, Grafana Assistant.

### Full stack (later)
Add Drain3 templating plus pgvector `error_signatures` (local embeddings), then DeepEval/Inspect judge runs written to `evals` with a human-label calibration set, then the scorecard-driven router (section 8), then mcp-grafana read-only for metrics and logs. Optionally add HolmesGPT (read-only, local model) if the infrastructure moves to Kubernetes, and Langfuse self-hosted if a trace or eval UI is needed. Avoid Phoenix (ELv2) and Grafana Assistant/Sift (Grafana Cloud link) because of the open-source and third-party constraints.

### What would change these verdicts
- Choosing **ClickHouse or SigNoz** as the main backend: then use their MCP servers (read-only user) and Langfuse becomes cheap to add.
- Grafana publishing an **open-source, fully local** Assistant: then re-evaluate it.
- Household consent to send redacted telemetry to a hosted model: hosted RCA becomes the default for quality.
- Telemetry volume growing to product or multi-tenant scale: ML anomaly detection and a dedicated eval platform become worthwhile.
