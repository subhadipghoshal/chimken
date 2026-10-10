# Telemetry storage / database review (as of 2026-10-10)

Scope: where Chimken telemetry (logs, metrics, traces, LLM/agent spans) is stored. Constraints: Apache-2.0 public repo,
single homelab host, ADR 002 (add infra only on proven need), Postgres + pgvector default, one backup/restore target,
sensitive telemetry never in Git, possible future product. Labels: FACT = verified at the cited source this session
(license files read from raw.githubusercontent.com on 2026-10-10); INFERENCE = reviewer judgement.

## 1. License check (product risk)

| Store | License (verified) | Product risk | Source | Label |
|---|---|---|---|---|
| ClickHouse | Apache-2.0 | Low | https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/LICENSE | FACT |
| HyperDX (ClickStack UI) | MIT | Low | https://raw.githubusercontent.com/hyperdxio/hyperdx/main/LICENSE | FACT |
| SigNoz | MIT outside `ee/` and `cmd/enterprise/`; those have a separate EE license | Medium: check which features are in `ee/` | https://raw.githubusercontent.com/SigNoz/signoz/main/LICENSE | FACT |
| PostgreSQL extensions: pgvector, pg_partman | PostgreSQL License | Low | https://raw.githubusercontent.com/pgvector/pgvector/master/LICENSE , https://raw.githubusercontent.com/pgpartman/pg_partman/master/LICENSE.txt | FACT |
| pg_duckdb | MIT | Low | https://raw.githubusercontent.com/duckdb/pg_duckdb/main/LICENSE | FACT |
| Citus | AGPL-3.0 | High for a closed hosted product, OK for self-use | https://raw.githubusercontent.com/citusdata/citus/main/LICENSE | FACT |
| TimescaleDB | Apache-2 core. Columnstore, continuous aggregates, retention policies, jobs and SkipScan are in the Community edition under the Timescale License (TSL). TSL bans offering it as a service. | High for a hosted product. Self-use is fine. | https://www.tigerdata.com/docs/about/latest/timescaledb-editions | FACT |
| Grafana Loki, Tempo, Mimir | AGPL-3.0 (Grafana relicensed in 2021) | High if modified and offered over a network. Unmodified self-hosting is fine. | https://raw.githubusercontent.com/grafana/loki/main/LICENSE , https://raw.githubusercontent.com/grafana/tempo/main/LICENSE , https://raw.githubusercontent.com/grafana/mimir/main/LICENSE , https://grafana.com/blog/2021/04/20/qa-with-our-ceo-on-relicensing/ | FACT |
| Prometheus | Apache-2.0 (CNCF) | Low | https://github.com/prometheus/prometheus | FACT (well-known, not re-fetched) |
| VictoriaMetrics, VictoriaLogs, VictoriaTraces | Apache-2.0 (single-node and cluster). Enterprise features are licensed separately. | Low for the core. Watch the enterprise feature line. | https://raw.githubusercontent.com/VictoriaMetrics/VictoriaLogs/master/LICENSE , https://docs.victoriametrics.com/victorialogs/ | FACT |
| GreptimeDB | Apache-2.0. v1.0 GA on 2026-04-14. There is a separate Enterprise product. | Low to medium (open-core) | https://raw.githubusercontent.com/GreptimeTeam/greptimedb/main/LICENSE , https://greptime.com/blogs/2026-04-14-greptimedb-v1-ga-release | FACT |
| OpenObserve | AGPL-3.0 since Nov 2023 (was Apache-2.0) | High; it has relicensed once already | https://raw.githubusercontent.com/openobserve/openobserve/main/LICENSE , https://openobserve.ai/blog/what-are-apache-gpl-and-agpl-licenses-and-why-openobserve-moved-from-apache-to-agpl.md | FACT |
| Quickwit | Apache-2.0. Datadog acquired it in Jan 2025 and relicensed it, but the team now works on Datadog products. | Low license risk, high abandonment risk | https://raw.githubusercontent.com/quickwit-oss/quickwit/main/LICENSE , https://www.datadoghq.com/blog/datadog-acquires-quickwit/ , https://quickwit.io/blog/quickwit-joins-datadog | FACT for the license. INFERENCE for the maintenance risk; I could not check commit activity because the GitHub API was blocked. |
| DuckDB, DuckLake, Iceberg | MIT (DuckDB), Apache-2.0 (Iceberg). DuckLake 1.0 shipped 2026-04-13 and can use a Postgres catalog. | Low | https://ducklake.select/2026/04/13/ducklake-10/ , https://duckdb.org/2025/11/28/iceberg-writes-in-duckdb.html | FACT for releases. INFERENCE for the DuckLake license (MIT, not re-fetched). |

No candidate uses the SSPL or BSL licenses. Elasticsearch/OpenSearch were out of scope. The license traps are AGPL (the LGTM stack, OpenObserve, Citus) and source-available licenses (TimescaleDB TSL, the SigNoz `ee/` directory).
**Verdict changes if:** the product will never be offered as a hosted or network service. In that case AGPL only constrains distributing modifications, and LGTM becomes acceptable.

## 2. Capability comparison

| Option | Signals | Query language (LLM fit) | Single-node footprint | Retention / TTL | Backup | Ops burden | Label / source |
|---|---|---|---|---|---|---|---|
| Postgres (same instance), native partitioning + pg_partman | Anything you model: runs, spans, events, logs. Metrics are awkward. | SQL; best for LLM generation; direct join to `runs` | Already running, so zero extra | Drop daily partitions (cheap) | Same pg_dump/pgBackRest; one target | Lowest at small scale | INFERENCE |
| Postgres + TimescaleDB | Time series, compressed | SQL | Small | `add_retention_policy` (TSL) | Same as PG | Low | FACT on TSL features: https://www.tigerdata.com/docs/about/latest/timescaledb-editions |
| Postgres + pg_duckdb | Analytical queries over PG tables, or Parquet in object storage | SQL | Small | Via Parquet files | Parquet copies | Low to medium | INFERENCE (MIT confirmed above) |
| ClickHouse + OTel exporter (ClickStack) | Logs, traces, metrics, session replay | SQL (ClickHouse dialect); good LLM fit | 4 GB minimum, 8 GB+ in practice, 4+ cores, SSD. Merge-memory tuning needed. | Native `TTL` plus `PARTITION BY toDate`. Exporter default is 72 h, with `ttl_only_drop_parts=1`. | `BACKUP` to disk or S3; second backup target | Medium | FACT: https://clickhouse.com/docs/observability/integrating-opentelemetry , https://altinity.com/blog/deploying-single-node-clickhouse-on-small-servers |
| SigNoz (on ClickHouse) | Logs, metrics, traces | Query builder, ClickHouse SQL, PromQL | ClickHouse plus a ZooKeeper/Keeper and app services, so heavier than ClickHouse alone | Configurable | Same as ClickHouse | Medium to high | INFERENCE |
| LGTM (Loki, Mimir/Prometheus, Tempo) | Logs, metrics, traces in 3 stores | LogQL, PromQL, TraceQL; three DSLs; weaker LLM fit and no joins | 3 or more services | Per-store config | 3 stores, plus object storage | High | INFERENCE |
| VictoriaMetrics, VictoriaLogs, VictoriaTraces | Metrics, logs, traces | MetricsQL, LogsQL (has a SQL-to-LogsQL guide); no SQL | Very small; vendor claims up to 30x less RAM than Loki/ES | `-retentionPeriod` (default 7d) or disk-usage caps | Per-partition snapshot plus rsync | Low per component, but 3 components | FACT: https://docs.victoriametrics.com/victorialogs/ ; VictoriaTraces is still 0.x (https://newreleases.io/project/github/VictoriaMetrics/VictoriaTraces/release/v0.10.0) |
| GreptimeDB | Metrics, logs, traces in one engine | SQL plus PromQL | Rust single binary; local disk or object storage | TTL per table | Object storage | Low to medium; young (GA Apr 2026) | FACT: https://greptime.com/blogs/2026-04-14-greptimedb-v1-ga-release ; footprint is INFERENCE |
| OpenObserve | Logs, metrics, traces (Parquet on object storage) | SQL plus PromQL | Small | Yes | Object storage | Low | AGPL (FACT); other details INFERENCE |
| Parquet + DuckLake/Iceberg + DuckDB | Cold archive or analytics for any signal | SQL | Files only | Delete or expire snapshots | Copy files plus catalog | Low, but no live ingest/UI | FACT: https://ducklake.select/2026/04/13/ducklake-10/ |
| Quickwit | Logs, traces | Elasticsearch-like DSL | Small | Yes | Object storage | Low, but upstream is risky | See section 1 |

### Why SQL matters for AI-native telemetry (INFERENCE)
- LLMs have far more SQL in their training data than LogQL, TraceQL or MetricsQL. SQL also lets one query join telemetry with `runs`, `tasks` and pgvector tables. Three DSLs mean three prompt contracts and no cross-signal joins.
- SQL stores can be checked mechanically. You can run `EXPLAIN`, use read-only roles and add row limits, which provides guardrails for agent-written queries.
- PromQL is still the lingua franca for metric alerting. Keep the PromQL option open through GreptimeDB or ClickHouse's Prometheus compatibility rather than making it the primary interface.
- **Verdict changes if:** a mature MCP/LLM tool emerges that translates reliably into LogQL/TraceQL, or Grafana ships a SQL layer over LGTM.

## 3. Cost at two scales (INFERENCE unless cited)

| Scale | Postgres | ClickHouse | LGTM / Victoria | Object store + DuckDB |
|---|---|---|---|---|
| Homelab, under 5 GB/day raw (realistically under 100 MB/day for agent runs) | Rows plus JSONB plus indexes take roughly 1-3x raw on disk. At under 100 MB/day with 30-day retention, that is a few GB, which is trivial. Writes cost about 1 WAL write per row. Batch inserts keep this fine well below 1k rows/s. | Columnar ZSTD typically compresses 5-15x. It needs a dedicated 4-8 GB of RAM, which is idle overhead at this volume. | Light per service, but you run 3 services plus dashboards | Near-zero compute. Query latency is seconds. |
| Product scale, 100 GB-1 TB+/day | Row store, indexes, vacuum and WAL become the bottleneck. Citus adds AGPL. Not recommended. | Built for this. Many vendors run on it (ClickStack, SigNoz, and others). | Viable. Mimir/Loki/Tempo are proven at scale but AGPL. Victoria is Apache. | Good for the cold tier and long retention |

## 4. Same Postgres as app data, or a separate store?

**Recommendation: same Postgres instance now, with an exit seam built in.** (INFERENCE)

| Reason | Detail |
|---|---|
| ADR 002 / no proven need | There is no telemetry workload yet. The `runs` table is already planned in Postgres. |
| Single backup target | One pgBackRest/pg_dump drill covers app data and telemetry. Sensitive telemetry stays in the data layer, out of Git. |
| Joins and RAG | Span and event text joins `runs` directly. pgvector embeddings of failures and transcripts sit next to them. |
| Seam | Put telemetry in a separate schema (`telemetry`) with its own role, and partition append-only tables daily (native `PARTITION BY RANGE`; add pg_partman only if manual partition creation becomes painful). Retention is `DROP` partition. Shape columns after the OTel GenAI/trace model (`trace_id`, `span_id`, `parent_span_id`, `name`, `start/end`, `attributes jsonb`) so export to ClickHouse later is a copy job, not a redesign. |

**Move telemetry to a separate store when any of these is measured (thresholds are INFERENCE):**
1. Telemetry ingest exceeds about 1-5 GB/day sustained, or about 50M rows per month.
2. Telemetry writes or vacuum measurably degrade app p95 latency, or WAL/backup size is more than 70% telemetry.
3. Infrastructure, host or container logs and metrics are needed, not just agent run spans. These are high volume, need full-text search, and have high-cardinality metrics.
4. You need an off-the-shelf trace UI (waterfalls, service maps) that would be costly to rebuild.
5. The product track starts and needs a multi-tenant telemetry plane.

Intermediate step before a new server: put the telemetry schema in a second Postgres database on the same cluster, or add pg_duckdb plus Parquet/DuckLake (with the Postgres catalog) for the cold tier. Both keep a single backup tool.

## 5. Store-specific notes

- **ClickHouse OTel schema (FACT, https://clickhouse.com/docs/observability/integrating-opentelemetry):**
  - Tables are `otel_logs` and `otel_traces`, using MergeTree, `PARTITION BY toDate(Timestamp)`, and `Map(LowCardinality(String),String)` columns for attributes.
  - The default ORDER BY is `(ServiceName, SpanName/SeverityText, ts, TraceId)`.
  - ZSTD(1) compression, with Delta for timestamps.
  - Docs recommend `create_schema=false` and managing DDL yourself.
  - Agent attributes in a Map are slow to filter. Promote hot GenAI attributes such as `gen_ai.request.model`, token counts and `run_id` to materialized columns (INFERENCE).
- **Joining ClickHouse to the Postgres `runs` table:** use ClickHouse's `postgresql()` table function or a PostgreSQL table engine, or replicate `runs` into ClickHouse. The table function is a FACT (well-known, not re-fetched): https://clickhouse.com/docs/engines/table-engines/integrations/postgresql
- **ClickStack/HyperDX:** ClickHouse acquired HyperDX on 2025-03-13 and maintains the ClickHouse OTel exporter. HyperDX is MIT. FACT: https://clickhouse.com/blog/clickhouse-acquires-hyperdx-the-future-of-open-source-observability
  - Risk (INFERENCE): the UI is vendor-steered, but the storage stays plain ClickHouse tables, so the UI can be swapped without migrating data.
- **TimescaleDB:** the features most useful for telemetry (columnstore, continuous aggregates, retention policies) are TSL. That is fine for the homelab, but a product would have to avoid them or buy a license. Native partitioning plus pg_partman covers retention with no license risk (FACT on the features; INFERENCE on the substitute).
- **Quickwit:** the license is fine (Apache-2.0), but the team moved to Datadog (FACT). Do not adopt it for a new build unless commit activity in 2026 shows active maintenance (INFERENCE; not checked).
- **OpenObserve:** technically attractive (Parquet, SQL). However, AGPL plus a past relicense makes it a poor base for a future product (INFERENCE).
- **GreptimeDB:** the closest match to the brief on paper: Apache-2.0, SQL plus PromQL, one engine for all signals, object storage. It is also the youngest, GA in Apr 2026. It is the runner-up to ClickHouse (INFERENCE). **Verdict changes if** it proves stable in a homelab soak, or its enterprise line pulls in core features.

## 6. Recommendation

**Minimal first slice (ADR 002 compliant; no new infrastructure):**
1. In the existing Postgres, create schema `telemetry` with:
   - `runs`, which is app-owned and already planned
   - `telemetry.spans` (OTel-shaped, `attributes jsonb`, `run_id` FK-by-value, partitioned by day)
   - `telemetry.events` (logs and tool calls)
   - optional pgvector embeddings of failure summaries
2. Retention is a scheduled `DROP` of old partitions (for example 30-90 days). Backup is the existing PG backup and restore drill.
3. Write through an OTel SDK in the Python agents. Exporting can be a tiny in-repo OTLP-to-Postgres writer, or direct inserts at the start. Keep the OTel data model so the destination can be swapped. (INFERENCE: I did not confirm a maintained upstream OTel Collector Postgres exporter, so verify before depending on one.)
4. LLM access is a read-only SQL role, with query limits.

**Full stack (when a section 4 trigger fires):**
- OTel Collector writes to **ClickHouse** (Apache-2.0, single node, native TTL, its own BACKUP to the same backup host or bucket).
- **HyperDX/ClickStack** (MIT) or Grafana with the ClickHouse datasource for the UI.
- Postgres stays the system of record for `runs`/RAG. ClickHouse joins via `postgresql()` or a replicated `runs` dimension.
- Cold archive goes to Parquet/DuckLake with the Postgres catalog for long retention.
- Avoid AGPL (LGTM, OpenObserve, Citus) and TSL-only features in anything the product might host.
- Runner-up: GreptimeDB. Choose it instead if PromQL-native metrics plus SQL in one Apache binary matters more than ecosystem maturity.

**What would flip the whole verdict:**
- Measured volume is 10x the estimate from day one: go straight to ClickHouse.
- The product is never hosted, so AGPL is acceptable: LGTM becomes viable for its UI.
- ClickHouse or HyperDX relicenses to a non-OSI license: switch to GreptimeDB or the Victoria stack.
- GreptimeDB or DuckLake reach clear operational maturity: re-evaluate the runner-up.

Verification gaps: the GitHub API was blocked (403), so repository activity (Quickwit and SigNoz `ee/` scope) and the OTel Postgres exporter were not confirmed. Compression ratios and footprint figures are typical values, not benchmarks run here.
