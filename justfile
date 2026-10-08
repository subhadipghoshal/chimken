# Run from the repository root. Equivalent uv commands are in CONTRIBUTING.md.
default:
    @just --list

setup:
    uv sync --all-packages --locked

check:
    uv run --all-packages --locked ruff check .
    uv run --all-packages --locked ruff format --check .
    uv run --all-packages --locked mypy
    uv run --all-packages --locked pytest
    uv run --all-packages --locked python scripts/check_repository.py
    uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json

demo:
    uv run --all-packages --locked chimken-lab triage workflows/oss-contributions/example.json

eval:
    uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json

format:
    uv run --all-packages --locked ruff format .

