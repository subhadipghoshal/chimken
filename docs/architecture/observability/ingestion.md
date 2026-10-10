# Observability: data ingestion review (as of 2026-10-10)

Scope: how telemetry (logs, metrics, traces, LLM/agent traces) gets from Chimken agents and
host into the data layer. Tags: **FACT** = read from the cited source this session;
**INFERENCE** = reviewer judgement or prior knowledge not re-verified. GitHub API was blocked in
this session, so release data comes from release pages, vector.dev and PyPI.

## 1. Bottom line

- Use **OTLP everywhere** as the one wire format. Every source that matters already emits it:
  Claude Code, Codex CLI, OTel Python SDK, OpenLLMetry, and OpenInference.
- Put **one OpenTelemetry Collector** in front as the redaction, sampling and buffering point.
  Build a custom distribution with `ocb` that keeps only the contrib components you need.
- Treat **gen_ai.* semconv as unstable**. Store raw attributes and normalise at query time.
- Skip **Vector**: it is Datadog-owned, pre-1.0, and has partial OTLP sink support.
- Skip **Fluent Bit** unless you need to tail lots of host logs.
- Consider **Alloy** only if the backend ends up being the Grafana LGTM stack.

## 2. Agent and SDK emitters

| Source | What it emits | Content defaults | Evidence |
|---|---|---|---|
| Claude Code | Metrics (`claude_code.token.usage`, `cost.usage`, `session.count`, ...)<br>Log events (`user_prompt`, `tool_result`, `tool_decision`, `api_request`, `api_error`, ...)<br>Traces in **beta**, gated by `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` + `OTEL_TRACES_EXPORTER`; spans `claude_code.interaction` > `llm_request` / `tool` / `hook` | Enabled with `CLAUDE_CODE_ENABLE_TELEMETRY=1` + standard `OTEL_*` exporters.<br>Prompts and responses are **redacted** by default.<br>Tool input, tool output and raw API bodies are **off** by default; opt in with `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, `OTEL_LOG_RAW_API_BODIES` | FACT: https://code.claude.com/docs/en/monitoring-usage |
| Codex CLI | `[otel]` in `config.toml`, **off by default**, with `otlp-http` or `otlp-grpc` exporters.<br>Log events: `codex.conversation_starts`, `api_request`, `sse_event` (tokens), `user_prompt`, `tool_decision`, `tool_result`.<br>Docs also mention metrics; trace export is not documented | `log_user_prompt=false` by default.<br>`tool_result` includes an **output snippet** | FACT: https://learn.chatgpt.com/docs/config-file/config-advanced (redirected from developers.openai.com/codex/config-advanced) |
| Gemini CLI, Grok | Not verified this session | n/a | INFERENCE: Gemini CLI has OTel export per its docs; verify before relying on it |
| OTel Python SDK | `opentelemetry-sdk` 1.45.1 (2026-10-06); `opentelemetry-distro` 0.66b1 | n/a | FACT: PyPI JSON |
| OTel GenAI instrumentations (official) | `opentelemetry-instrumentation-openai-v2` 2.4b0 (2026-05)<br>`-google-genai` 1.2b0 (2026-09)<br>`opentelemetry-util-genai` 1.2b0<br>`-openai-agents-v2` 0.1.0 (2025-10, stale) | All beta. Content capture is opt-in (`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`) | FACT: PyPI; capture flag from https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained |
| OpenLLMetry (Traceloop) | `traceloop-sdk` 0.62.4 (2026-09-29), Apache-2.0.<br>Covers Anthropic, OpenAI, Gemini, Vertex; xAI not listed.<br>SDK self-telemetry removed from v0.49.2 | Content tracing is on unless disabled (INFERENCE: `TRACELOOP_TRACE_CONTENT=false`) | FACT: https://raw.githubusercontent.com/traceloop/openllmetry/main/README.md and PyPI |
| OpenInference (Arize) | `openinference-instrumentation-anthropic` 3.0.3 and `-claude-agent-sdk` 0.1.21, both released 2026-10, Apache-2.0.<br>Also covers OpenAI, Google GenAI, OpenAI Agents and MCP | Masking via `OPENINFERENCE_HIDE_*` env vars (FACT for Go; INFERENCE for Python) | FACT: https://raw.githubusercontent.com/Arize-ai/openinference/main/README.md and PyPI |

### Notes on the emitters

- **PyPI name collision (FACT).** The PyPI package named `opentelemetry-instrumentation-anthropic` is published by Traceloop, not by the OTel project. Pin the right package deliberately.
- **Traceloop ownership (FACT).** ServiceNow announced it is acquiring Traceloop (reported 2026-03-03): https://entrepreneurloop.com/servicenow-acquires-traceloop-ai-governance-acquisition/
- **OpenLLMetry future (INFERENCE).** OpenLLMetry's long-term stewardship is a risk. Prefer the official OTel GenAI instrumentations where they exist, and OpenInference where they don't (for example the Claude Agent SDK).
- **Gap in the agent CLIs (INFERENCE).** Neither Claude Code nor Codex emits `gen_ai.*` semconv names. Both use vendor namespaces (`claude_code.*`, `codex.*`), so normalising them into one "runs" view is Chimken's job, done in the Collector (transform/OTTL) or at query time.
  - What would change this: either vendor adopting `gen_ai.*` agent spans.

## 3. GenAI semantic conventions status

| Point | Status | Evidence |
|---|---|---|
| Stability | All `gen_ai.*` spans, metrics and attributes are **Development** as of Sept 2026. Only inherited core attributes (`error.type`, `server.*`) are Stable | FACT (secondary source): https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained |
| Repository | Moved to `open-telemetry/semantic-conventions-genai` in v1.42.0 (June 2026). The new repo has no tagged release | FACT: https://opentelemetry.io/docs/specs/semconv/gen-ai/ and https://github.com/open-telemetry/semantic-conventions-genai |
| Span shapes | `chat {model}`, `invoke_agent {name}`, `execute_tool {tool}`; MCP conventions exist | FACT: dash0 page above; semconv index |
| Content placement | Prompts and completions go in event `gen_ai.client.inference.operation.details` (`gen_ai.input.messages` / `gen_ai.output.messages`), not span attributes | FACT: dash0 page above |

Implications:

- **Expect renames (INFERENCE).** Keep the raw OTLP payload, either as Postgres JSONB or in the backend's native store, plus a thin versioned mapping layer. Do not hard-code `gen_ai.*` column names into the `runs` schema.
  - What would change this: a Stable release of the GenAI conventions.
- **Content placement is good for privacy (INFERENCE).** Because content travels as an event, the Collector can route or drop content events separately from spans.

## 4. Collectors and agents compared

| Option | License / governance | Health | OTLP | Redaction at the edge | Sampling | Buffering / backpressure | Single-node footprint | Lock-in |
|---|---|---|---|---|---|---|---|---|
| **OTel Collector core** (`otelcol`) | Apache-2.0, CNCF (OTel is Incubating, INFERENCE) | Still 0.x. Releases about every 2 weeks: v0.160.0 (09-02), v0.161.0 (09-16), v0.162.0 (09-29) (FACT, releases page) | Native in and out | Core only has basic processors; no redaction | Probabilistic needs contrib | `sending_queue` + `retry_on_failure`; persistent queue via `storage: file_storage`; `block_on_overflow` (FACT, exporterhelper README) | Small. INFERENCE: tens of MB RSS | Lowest |
| **OTel Collector contrib** / custom `ocb` build | Same as core | Same as core | Native | `redaction` processor: allowlist keys, regex `blocked_values`, `blocked_key_patterns`, HMAC hashing. Stability: traces **beta**, logs and metrics **alpha** (FACT, redactionprocessor README).<br>Plus `attributes`, `transform` (OTTL), `filter` (INFERENCE) | `tail_sampling` (traces, **beta**, stateful; all spans of a trace must hit one instance; `num_traces` 50k, `decision_wait` 30s) (FACT, tailsamplingprocessor README) | Same as core | Full contrib binary is large (INFERENCE: ~hundreds of MB). An `ocb` build is what the docs recommend for smaller binaries (FACT: https://opentelemetry.io/docs/collector/distributions/) | Low |
| **OpAMP** (fleet management) | Apache-2.0, OTel | Supervisor ships as `cmd/opampsupervisor`; the docs call OpAMP "an emerging standard" (FACT: https://opentelemetry.io/docs/collector/management/) | n/a | n/a | n/a | n/a | n/a | Low.<br>INFERENCE: not needed on a single host; relevant only if Chimken becomes a product with many agents |
| **Grafana Alloy** | Apache-2.0 (INFERENCE), Grafana Labs | v1.19.0 to v1.19.2 released Aug 2026 (FACT, releases page) | Yes. Alloy is "an OpenTelemetry Collector distribution" with `otelcol.*` components (FACT: https://grafana.com/docs/alloy/latest/introduction/) | Through wrapped `otelcol.processor.*` components (INFERENCE: coverage lags contrib) | Wrapped tail sampling (INFERENCE) | Inherits from the Collector (INFERENCE) | Moderate | Medium: Alloy-specific config syntax; strongest with Loki, Mimir, Tempo, Pyroscope |
| **Vector** | **MPL-2.0** (FACT, LICENSE). Owned by Datadog (FACT: "© 2026 Datadog" footer, https://vector.dev/releases/) | Still 0.x, releases about every 6 weeks: 0.59.0 (2026-10-06) (FACT) | `opentelemetry` source decodes OTLP logs, metrics and traces (0.50); `otlp` codec (0.51); sink started as logs-only OTLP/HTTP (0.43) and its later scope is unclear (FACT, release notes) | VRL remaps are powerful (INFERENCE) | Not trace-aware (INFERENCE) | Disk buffers (INFERENCE) | Small, Rust (INFERENCE) | Medium: VRL; vendor steering toward Datadog Observability Pipelines (INFERENCE) |
| **Fluent Bit** | Apache-2.0. Under the CNCF-graduated Fluentd umbrella (Fluentd graduated 2019-04-11 per https://www.cncf.io/projects/fluentd/ (FACT); Fluent Bit's place under it is INFERENCE) | 5.1.2 and 5.0.10 released Sept, two maintained release lines (FACT, releases page) | Has OTLP input and output (INFERENCE) | Lua and modify filters (INFERENCE) | None for traces (INFERENCE) | Filesystem buffering (INFERENCE) | Very small: C, a few MB (INFERENCE) | Low.<br>Logs-first; weak for traces and agent spans (INFERENCE) |

## 5. Cross-cutting concerns

### PII redaction at the edge (priority 1 for Chimken)

- **Layer 1, source defaults (FACT).** Leave Claude Code's content flags unset and keep Codex `log_user_prompt=false`.
- **Layer 2, Collector processing (FACT for the processor's capabilities).**
  - Run the `redaction` processor in allowlist mode, plus `transform` / OTTL to drop attributes such as `tool.output` and `gen_ai.*.messages`.
  - Use HMAC hashing for identifiers so records can still be joined without exposing values.
  - Caveat (INFERENCE): the processor is alpha for logs. Agent CLI content mostly travels as **log events**, so test the redaction rules with fixtures in CI.
- **Codex tool output leak (INFERENCE).** Codex `tool_result` carries an output snippet even with prompt logging off. Drop or truncate it in the Collector, since household data could leak through it.
- **Content you deliberately keep (INFERENCE).** If you want prompts for AI analysis, route them through a separate pipeline to Postgres or the data layer with its own retention. Never send them to anything Git-adjacent.

### Sampling

- **Keep everything at first (INFERENCE).** At household scale, keeping 100% of traces is cheap. Tail sampling adds statefulness, a 30s decision delay and beta risk.
- **Add tail sampling later (INFERENCE).** Only when volume proves the need (ADR 002). Then use rules such as "keep errors, slow traces and expensive runs; sample the rest".

### Buffering and backpressure

- **Collector setup (FACT for options; settings are a recommendation).** Use `file_storage` persistent queue + `retry_on_failure`, and set `max_elapsed_time: 0` for the run-log pipeline so data survives a database outage or restart. Add `memory_limiter` (INFERENCE; not documented in that README).
- **SDK side (FACT).** Codex batches asynchronously and flushes on shutdown. INFERENCE: short-lived CLI runs can lose data if they are killed, so point them at a localhost Collector, never straight at a remote backend.

### Lock-in

- **OTLP plus an OTel Collector config is the most portable choice (INFERENCE).**
- Vector's VRL and Alloy's syntax are proprietary configuration surfaces, even though both are open source.
- OpenInference and OpenLLMetry attribute names differ from `gen_ai.*`. Pick one in-process convention and convert in the Collector if needed.

## 6. What would change the verdict

| Trigger | New verdict |
|---|---|
| Backend chosen is Grafana LGTM | Alloy becomes reasonable, though it is still optional |
| Heavy host and container log tailing appears (many files, journald) | Add Fluent Bit or the Collector's `filelog` / `journald` receivers. INFERENCE: try the Collector receivers first |
| Datadog relicenses Vector or reaches 1.0 with full OTLP sink | Re-evaluate Vector; no change while it is pre-1.0 |
| GenAI semconv reaches Stable, or Claude Code / Codex emit `gen_ai.*` | Map directly into typed `runs` columns instead of JSONB + mapping |
| Chimken becomes a multi-tenant product | Add OpAMP fleet management, a gateway tier, and load-balancing exporter + tail sampling |
| Traceloop/ServiceNow stops maintaining OpenLLMetry | Already hedged by preferring official OTel GenAI instrumentation and OpenInference |

## 7. Recommendation

### (a) Minimal first slice (one host, ADR 002-compliant)

1. **One Collector on localhost.** Run a custom `ocb` build, or `otelcol-contrib` pinned to a version until the build is worth doing.
   - Receivers: `otlp` (gRPC :4317 / HTTP :4318), bound to localhost only.
   - Processors: `memory_limiter`, `redaction` (allowlist), `transform` (drop content attributes and truncate Codex `tool_result` snippets), `batch`.
   - Exporters: one to the chosen backend, or to Postgres via a small OTLP-to-`runs` writer. Use a `file_storage` persistent queue.
2. **Agent CLIs.**
   - Claude Code: `CLAUDE_CODE_ENABLE_TELEMETRY=1`, metrics and logs as OTLP to localhost, content flags off. Traces only after the beta proves useful.
   - Codex: `[otel] exporter = otlp-grpc` to localhost, `log_user_prompt=false`.
3. **Chimken's own Python code.**
   - Use the `opentelemetry-sdk` with one root span per run carrying `run.id`.
   - The `run.id` links the OTLP traces to the Postgres `runs` row.
   - Instrument LLM calls with the official `opentelemetry-instrumentation-*-v2` / `google-genai` packages, with content capture off.
4. **Tests.** Add a CI fixture that sends a sample event with fake PII through the Collector config and asserts that it was redacted.
5. **Not in the first slice:** tail sampling, OpAMP, Alloy, Vector, Fluent Bit, Kafka.

### (b) Full stack (when the workloads prove the need)

- **Two-tier Collector.**
  - Agent tier: per host, doing redaction and buffering.
  - Gateway tier: `loadbalancing` exporter, then `tail_sampling`, `spanmetrics` / connectors, then fan-out to the backends: traces and logs store, metrics TSDB, Postgres/pgvector for run summaries and embeddings.
- **Content pipeline.** A separate, consented pipeline that sends prompts and tool output to the data layer, using GenAI content events, with retention and RBAC.
- **Instrumentation.** OpenInference for agent frameworks that official OTel does not cover, such as the Claude Agent SDK. Normalise to `gen_ai.*` in a versioned OTTL transform.
- **Fleet management.** OpAMP supervisor, only if Chimken grows into a multi-host product.
- **Host logs.** `filelog` / `journald` receivers in the Collector, with Fluent Bit only if they can't keep up.
