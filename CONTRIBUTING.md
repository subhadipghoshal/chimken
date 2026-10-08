# Contributing

Small, reviewable pull requests are welcome. Start with a GitHub Issue when work needs coordination. Keep an issue and pull request focused on one outcome.

Use Python 3.12+ and `uv` from the repository root:

```sh
uv sync --all-packages --locked
uv run --all-packages --locked ruff check .
uv run --all-packages --locked ruff format --check .
uv run --all-packages --locked mypy
uv run --all-packages --locked pytest
uv run --all-packages --locked python scripts/check_repository.py
uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json
```

`just check` runs the same checks when [just](https://just.systems/) is installed. `just demo` runs the example triage command.

Preserve the licenses of external material. Verify provenance and sanitize content before any public upload. Do not add secrets, private household data, runtime state, or external OSS clones to the repository.
