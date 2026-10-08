# OSS-triage contract

`chimken-lab triage INPUT` loads one JSON object and prints one JSON result to stdout. `chimken-lab evaluate INPUT` loads a synthetic suite and prints a JSON report to stdout. Inputs are local files of at most 1 MiB. Duplicate JSON keys are rejected. Neither command makes network requests, model calls, or grants authorization.

## Triage input

The input object has exactly these fields:

| Field | Type and allowed values |
| --- | --- |
| `schema_version` | integer, exactly `1` |
| `state` | string: `open` or `closed` |
| `kind` | string: `docs`, `bug`, or `feature` |
| `complexity` | string: `small`, `medium`, `large`, or `unknown` |
| `in_scope` | boolean |
| `requirements_clear` | boolean |
| `reproducer_present` | boolean |
| `tests_available` | boolean |
| `maintainer_welcome` | boolean |
| `risk_flags` | array of strings from `security`, `credentials`, `personal_data`, `breaking_change`, `dependencies`, `infrastructure`, `unclear_ownership` |

The success result has `schema_version` (integer `1`), `policy_version` (string), `route` (one of `ignore`, `research`, `design`, `agent_candidate`), `reason` (string), and `execution_authorized` (boolean `false`). A route is a recommendation, never permission to act.

## Evaluation input and result

The suite object has exactly `schema_version` (integer `1`) and `cases` (an array of 1 through 1000 items). Each case has exactly `id`, `facts`, and `expected`. `id` is a unique lowercase slug matching `[a-z0-9-]{1,80}`; `facts` is the triage object above; `expected` is a route string.

The result has `schema_version`, `runner_version`, `python_version`, `policy_version`, `dataset_sha256`, `cases`, `metrics`, `passed`, and `execution_authorized`. Each case result has `id`, `expected`, `actual`, `reason`, and `passed`. `metrics` has `total`, `correct`, `accuracy`, `false_agent_candidates`, `elapsed_seconds`, `model_calls` (integer `0`), and `model_cost_usd` (integer `0`). `execution_authorized` is always `false`.

## Exit and error codes

| Exit code | Meaning | stderr |
| --- | --- | --- |
| `0` | Valid triage, or an evaluation where every case passes | none |
| `1` | Valid evaluation with at least one mismatch | none |
| `2` | Input cannot be read or is invalid | `error: cannot read input file` or `error: invalid input; see docs/contracts/oss-triage.md` |

Invalid input includes files over 1 MiB, malformed JSON, duplicate fields, unsupported schemas, wrong or extra fields, wrong field types, invalid enum values, invalid IDs, duplicate IDs, and a suite outside the allowed case count.

`elapsed_seconds` measures the recommendation loop, excluding file reading, JSON parsing, and process startup. Timing varies across runs; routes, reasons, and correctness are deterministic. `python_version` records the interpreter version without machine identifiers. `model_cost_usd` covers model API spend only, not the cost of local compute or human work.

Malformed command-line arguments also exit `2`, with usage information and `chimken-lab: error: invalid arguments`. Errors never echo file contents or user-supplied paths. The JSON facts are manually assessed claims; accepting their schema does not establish that the claims are true.
