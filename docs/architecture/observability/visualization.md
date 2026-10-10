# Observability: Visualization and UI review (as of 2026-10-10)

Scope: which UI(s) Chimken should use for infra telemetry (logs/metrics/traces) and LLM/agent telemetry (span trees, tokens, cost, evals), given: Apache-2.0 public repo, single host, Postgres+pgvector default, ADR 002 (add infra only when a workload proves need), possible future productization.

Legend: **F** = FACT (verified at the cited URL on 2026-10-10). **I** = INFERENCE (my judgment, not stated by the source). "Flip" = what would change the verdict.

## 1. License and embedding/reselling

| Tool | License (F unless noted) | Embed/resell in a future Chimken product | Source | Flip |
|---|---|---|---|---|
| Grafana OSS | AGPLv3 (core Grafana, Loki, Tempo, since Apr 2021). Plugins, agents, some libraries stay Apache-2.0. "Unmodified distributions are not affected"; modifying and offering as a network service without releasing changes needs a paid licence. | I: Fine to run unmodified alongside a product. Forking/patching Grafana inside a hosted product triggers AGPL source obligations. Writing **plugins** (Apache) is the safe way to extend. | https://grafana.com/blog/2021/04/20/qa-with-our-ceo-on-relicensing/ , https://grafana.com/licensing/ | Grafana relicensing again, or Chimken needing to patch core. |
| Grafana ClickHouse datasource | Apache-2.0 | F: plugin is permissive. | https://github.com/grafana/clickhouse-datasource | - |
| HyperDX / ClickStack | MIT (root LICENSE). ClickStack = ClickHouse + HyperDX + OTel Collector + MongoDB. HyperDX acquired by ClickHouse Inc. (Mar 2025). | I: Most permissive infra-observability UI on the list; can be forked/embedded. | https://github.com/hyperdxio/hyperdx/blob/main/LICENSE , https://clickhouse.com/blog/clickhouse-acquires-hyperdx-the-future-of-open-source-observability | An `ee/` split appearing (not seen in root LICENSE; not fully audited). |
| SigNoz | MIT except `ee/` and `cmd/enterprise/` (governed by `ee/LICENSE`, proprietary). | I: Usable; embedding is safe only for the MIT parts. Need to check which features (SSO, etc.) sit in `ee/`. | https://github.com/SigNoz/signoz/blob/main/LICENSE | `ee/` growing to cover features Chimken needs. |
| Perses | Apache-2.0, CNCF **Sandbox**. npm packages for embedding panels and dashboards in other UIs. | F/I: The cleanest choice for embedding dashboards in a Chimken-owned UI. | https://github.com/perses/perses | Graduation progress or stalling; Sandbox means it is still early. |
| Jaeger v2 UI | Apache-2.0 (CNCF graduated). v2 is built on OTel Collector. UI moving to Zustand/React Query, adding an in-app AI assistant (AG-UI/ACP/MCP) and plans for GenAI semconv views (Apr 2026). | I: Permissive. Traces only; no metrics/logs dashboards. | https://thenewstack.io/jaeger-v2-ai-observability/ , https://github.com/jaegertracing/jaeger | GenAI views shipping (would make it a decent agent-trace viewer). |
| Apache Superset | Apache-2.0 | I: Embeddable, permissive; heavy (Python + Redis + metadata DB). | https://github.com/apache/superset | - |
| Metabase | AGPL (OSS edition). Embedding: comply with AGPL, or the Embedding License with the "Powered by Metabase" logo kept, or a commercial licence. Enterprise features need a commercial licence. | I: Avoid as a product-embedded surface; fine for internal analytics. | https://metabase.com/license | - |
| Langfuse | MIT except `ee/`, `web/src/ee/`, `worker/src/ee/`. Since Jun 2025, LLM-as-judge, annotation queues, prompt experiments, playground and SSO are MIT. EE = SCIM, audit logs, data retention, org creators, instance-management API, UI customization. **Acquired by ClickHouse Inc. on 2026-01-16**; core stays MIT. | I: Safe to self-host and to integrate via API. A hosted resale of Langfuse itself is MIT-allowed outside `ee/`. | https://raw.githubusercontent.com/langfuse/langfuse/main/LICENSE , https://langfuse.com/blog/2025-06-04-open-sourcing-langfuse-product , https://hackernoon.com/two-acquisitions-deep-two-still-standing-whats-really-happening-to-open-source-llm-observability | ClickHouse moving features into EE. |
| Arize Phoenix | **ELv2** (not OSI open source). "You may not provide the software to third parties as a hosted or managed service." Self-hosting is free with no feature gates. | F/I: Disqualifying for a future hosted Chimken product; fine for household use. Fails the "open source" requirement in the strict sense. | https://raw.githubusercontent.com/Arize-ai/phoenix/main/LICENSE , https://arize.com/docs/phoenix/self-hosting/license | Arize relicensing to OSI. |
| Opik (Comet) | Apache-2.0, no directory exceptions in root LICENSE. | I: Permissive. | https://raw.githubusercontent.com/comet-ml/opik/main/LICENSE | - |
| Helicone | Apache-2.0. **Acquired by Mintlify on 2026-03-03, maintenance mode** (no open-source/self-host commitment). Helm chart is enterprise-only. | I: Do not adopt (proxy-centric, maintenance mode). | https://github.com/Helicone/helicone , hackernoon link above | - |
| OpenLIT | Apache-2.0, OTel-native (GenAI semconv), ClickHouse storage. Traces, cost, GPU, 11 LLM-judge eval types, prompt hub. | I: Its SDK is useful even if its UI is not adopted. Grafana's own AI blog uses OpenLIT instrumentation. | https://github.com/openlit/openlit , https://grafana.com/blog/ai-observability-ai-agents | - |
| Laminar | OSS images (Compose); Signals, alerts and Slack need an `LMNR_LICENSE_KEY`. | I: Open-core with alerting gated; less attractive than Langfuse. | https://laminar.sh/docs/self-hosting | - |

## 2. Self-host footprint

| Tool | Required stores/services (F) | Fits Postgres-first single host? (I) |
|---|---|---|
| Grafana OSS | One binary plus SQLite or Postgres for metadata. Built-in Postgres datasource. | **Yes.** Lightest option; can query the Postgres `runs` table directly. |
| Perses | One Go binary plus file or SQL storage. | Yes, but **no Postgres/SQL datasource plugin** (plugins include ClickHouse, VictoriaLogs, Prometheus, Loki, Tempo, Jaeger, GreptimeDB, OpenSearch, Splunk, Pyroscope). Source: https://github.com/perses/plugins |
| HyperDX/ClickStack | ClickHouse + MongoDB + OTel Collector. | No. Brings in ClickHouse and Mongo; only justified once ClickHouse is adopted. |
| SigNoz | ClickHouse (+ Zookeeper/Keeper), query service, collector. | No. ClickHouse-only. |
| Jaeger v2 | One binary; storage plugin (memory/Badger/ES/Cassandra/ClickHouse via remote storage). | Yes for traces only (Badger on a single host). |
| Langfuse v3/v4 | Web + Worker + **Postgres + ClickHouse + Redis/Valkey + S3/blob** (https://langfuse.com/self-hosting). v4 (GA 2026-08-17) moves to a denormalized append-only observations table; v3 gets security patches until Jan 2027 (https://langfuse.com/changelog/2026-08-17-langfuse-v4.md). | **No for a first slice.** Five stateful dependencies. Justified only when trace volume or eval workflows prove need. |
| Opik | Java + Python backends, React frontend, **ClickHouse + MySQL + Redis + MinIO** (https://www.comet.com/docs/opik/self-host/architecture). | No. Adds MySQL to a Postgres shop. |
| Phoenix | Single container; SQLite or Postgres. | Yes technically, but license disqualifies (above). |
| OpenLIT | ClickHouse + OTel Collector + UI. | No. |
| Laminar | Compose: Postgres + ClickHouse + Quickwit; Helm adds RabbitMQ + Redis. | No. |
| Helicone | Supabase + ClickHouse + Workers + MinIO. | No. |
| Superset | Python app + metadata DB + Redis (+ Celery for async). | Heavyweight for one table. |
| Metabase | One JVM jar + metadata DB (Postgres). | Yes, but AGPL; overlaps Grafana. |

I: Every LLM-native UI except Phoenix requires **ClickHouse**. Choosing a dedicated LLM UI is, in practice, choosing ClickHouse. Langfuse and HyperDX now have the same owner (ClickHouse Inc.), which makes a ClickStack + Langfuse pairing coherent if ClickHouse is adopted later.

## 3. Dashboards-as-code in git

| Tool | Status | Source | F/I |
|---|---|---|---|
| Grafana | Git Sync GA on 2026-04-20 (Grafana v13.0.0) "for all Grafana Cloud and self-managed Grafana users", with GitHub/GitLab/Bitbucket/any git. Also file provisioning plus the Apache-2.0 Foundation SDK. | https://grafana.com/whats-new/2026-04-20-git-sync-for-grafana-dashboards-and-folders-now-generally-available/ | F (GA); I: OSS inclusion is implied by "self-managed" but not stated explicitly. File provisioning (JSON in repo, mounted read-only) works in OSS regardless. |
| Perses | Native: CUE and Go SDKs plus `percli`; designed for GitOps. | https://github.com/perses/perses | F |
| SigNoz | JSON dashboard import/export; the prebuilt AI dashboard cannot be edited or cloned. | https://signoz.io/docs/ai-observability/ | F (AI dashboard); I: weaker GitOps story |
| HyperDX | UI-first; no first-class as-code story found. | - | I |
| Langfuse / Opik / Phoenix | Dashboards are product views, not code. Configuration (prompts, eval configs) goes through API/SDK. | - | I |
| Superset / Metabase | Export/import of YAML/JSON; serialization in Metabase is an enterprise feature. | - | I (not re-verified) |

## 4. Agent-trace views (span tree, tokens, cost, evals)

| Tool | Span tree | Tokens/cost | Evals/scores | Notes |
|---|---|---|---|---|
| Langfuse | Yes (trace/observation tree, sessions) | Yes | Yes; LLM-as-judge, annotation queues, datasets/experiments (MIT) | I: Best fit for Chimken's ADR 003 (evaluations, bounded autonomy). |
| Opik | Yes | Yes | Yes (Python evaluator service) | - |
| Phoenix | Yes | Yes | Yes | ELv2 |
| Laminar | Yes, plus debugger, SQL-with-AI | Yes | Yes | Alerts gated |
| OpenLIT | Yes | Yes, plus GPU | 11 LLM-judge types | ClickHouse |
| SigNoz | Generic trace waterfall | Yes; prebuilt AI Overview (cost and tokens, TTFT, tool calls) from OTel GenAI attributes and `signozllmpricing` | **Not mentioned** | F: https://signoz.io/docs/ai-observability/ . I: The only infra APM that ships an AI dashboard in self-host. |
| Grafana OSS + Tempo | Generic trace view; no GenAI-aware rendering | Only via custom panels on span metrics or SQL | No native | F: Grafana's "AI/Agent Observability" (tokens, cost, online evals) is documented under **Grafana Cloud** and stores data in Grafana Cloud (https://grafana.com/docs/grafana-cloud/machine-learning/ai-observability/introduction.md). I: not available in OSS. |
| Jaeger v2 | Generic waterfall; GenAI semconv views planned | No | No | F (plans): thenewstack link |
| HyperDX | Generic waterfall + session replay | Via SQL charts | No | I |
| Perses | `tracingganttchart` / `tracetable` panels | Via queries | No | F (plugins exist) |

## 5. Can one UI serve infra and LLM telemetry?

| Option | Verdict | F/I |
|---|---|---|
| Grafana OSS alone | Covers infra fully and LLM **numbers** (tokens, cost, run outcomes, eval scores) via SQL on Postgres `runs`/`evals` tables. Lacks a GenAI-aware span tree, eval-annotation workflow and prompt/dataset management. | I |
| SigNoz alone | Closest to one UI: logs, metrics, traces plus a prebuilt AI cost/token dashboard. Lacks evals and annotation, requires ClickHouse, and its AI dashboard is not editable. | I (based on F docs) |
| Langfuse alone | LLM-only; no infra metrics or logs. | I |
| Practical answer | **Two surfaces, one data plane.** An infra UI plus an LLM UI, sharing OTel trace IDs and run IDs, with cross-links (e.g. Grafana data link → Langfuse trace URL). Every serious stack in this space looks like this; the AI-in-one tools are all Cloud-only (Grafana Cloud AI Observability) or ClickHouse-bound (SigNoz). | I |

## 6. Thin Chimken-owned UI (productization)

| Point | Assessment | F/I |
|---|---|---|
| Why | AGPL Grafana cannot be patched into a hosted product without source release; an LLM UI that is ELv2 (Phoenix) cannot be offered as a service at all. A product needs an owned surface for run/eval views that match Chimken's domain (household tasks, agents, bounded autonomy). | I |
| How | Keep it thin. Read the Postgres `runs`/`evals` tables plus OTel trace IDs; deep-link out to Grafana/Langfuse for drill-down. Embed **Perses** panels (Apache-2.0 npm packages) if charts are needed. | I; Perses embedding is F |
| When | Not now (ADR 002). Trigger: a second household or an external user, or a need for views that Grafana and Langfuse cannot express. | I |

## 7. Recommendation

### Minimal first slice (now, single host, Postgres-only)
1. **Grafana OSS** (unmodified, AGPL is fine for internal use) with the built-in **Postgres datasource** over the `runs` table (and later `evals`): run counts, success/failure by agent (Claude Code, Codex, Gemini, Grok), duration, tokens and cost columns, eval scores. Dashboards are JSON under `infra/observability/grafana/` via **file provisioning**. Git Sync is optional once confirmed in OSS v13.
2. **No dedicated LLM UI yet.** Emit OTel GenAI-semconv spans from agent runners (OpenLIT/OpenLLMetry SDKs are Apache-2.0) and store the `trace_id` on each `runs` row, so a trace UI can be added later without re-instrumenting.
3. If span trees are needed before ClickHouse: **Jaeger v2** (one binary, Badger storage) linked from Grafana via `trace_id`. This is the lowest-footprint trace view.

Rationale (I): zero new stateful stores, honors ADR 002 and the Postgres default, and everything is OTel-shaped so later choices stay open.

### Full stack (when trace volume or eval workflow proves need)
- **Data plane:** OTel Collector → ClickHouse (only if the storage review adopts it) or the LGTM/Victoria backends.
- **Infra UI:** Grafana OSS (Postgres + ClickHouse/Prometheus/Loki/Tempo datasources), dashboards in git. Alternative if ClickHouse becomes the single store: **HyperDX/ClickStack** (MIT) or SigNoz (MIT core).
- **LLM/agent UI:** **Langfuse** (MIT core, ClickHouse-owned, best eval/annotation workflow, v4 GA). Reuse the same ClickHouse; Postgres is already present. Prefer Opik only if Apache-2.0 matters more than footprint (it adds MySQL).
- **SQL analytics:** Grafana's SQL panels are enough. Add **Superset** (Apache-2.0) only if ad-hoc BI by non-engineers is needed. Avoid Metabase for anything that could be embedded (AGPL plus logo terms).
- **Product surface (later):** a thin Chimken UI that embeds Perses panels and deep-links to Langfuse/Grafana.
- **Excluded:** Phoenix (ELv2 blocks hosted resale), Helicone (maintenance mode after the Mintlify acquisition), Laminar (alerting is licence-gated).

### What would change this
- The storage review picks **ClickHouse** as primary → move the first slice to ClickStack + Langfuse sharing one ClickHouse, and drop Jaeger.
- The storage review picks **VictoriaMetrics/Logs** → Grafana or Perses (both have VictoriaLogs support) stay the infra UI.
- Grafana changes licence again, or Chimken needs to patch Grafana core → move dashboards to Perses.
- Langfuse moves eval or annotation features into EE after the ClickHouse acquisition → re-evaluate Opik.
- Phoenix moves to an OSI licence → it becomes the lightest LLM UI (single container on Postgres).
