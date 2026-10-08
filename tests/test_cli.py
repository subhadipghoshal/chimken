from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[1]
SOURCE_PATHS = (
    REPO_ROOT / "apps" / "lab" / "src",
    REPO_ROOT / "packages" / "oss-triage" / "src",
)

BASE_FACTS: dict[str, object] = {
    "schema_version": 1,
    "state": "open",
    "kind": "bug",
    "complexity": "small",
    "in_scope": True,
    "requirements_clear": True,
    "reproducer_present": True,
    "tests_available": True,
    "maintainer_welcome": True,
    "risk_flags": [],
}


def run_cli_args(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(os.fspath(path) for path in SOURCE_PATHS)
    return subprocess.run(
        [sys.executable, "-m", "chimken_lab.cli", *args],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def run_cli(command: str, input_path: Path) -> subprocess.CompletedProcess[str]:
    return run_cli_args(command, os.fspath(input_path))


def write_json(tmp_path: Path, value: object, name: str = "input.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def assert_invalid(result: subprocess.CompletedProcess[str], secret: str | None = None) -> None:
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: invalid input; see docs/contracts/oss-triage.md\n"
    if secret:
        assert secret not in result.stderr


def test_repository_triage_fixture_is_an_unauthorized_candidate() -> None:
    result = run_cli("triage", REPO_ROOT / "workflows" / "oss-contributions" / "example.json")

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "execution_authorized": False,
        "policy_version": "oss-triage-rules-v1",
        "reason": "bounded_candidate_pending_authorization",
        "route": "agent_candidate",
        "schema_version": 1,
    }


@pytest.mark.parametrize(
    "risk_flag",
    [
        "security",
        "credentials",
        "personal_data",
        "breaking_change",
        "dependencies",
        "infrastructure",
        "unclear_ownership",
    ],
)
def test_every_risk_flag_requires_human_design(tmp_path: Path, risk_flag: str) -> None:
    facts = {**BASE_FACTS, "risk_flags": [risk_flag]}

    result = run_cli("triage", write_json(tmp_path, facts))

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["route"] == "design"
    assert payload["reason"] == "risk_requires_human_design"
    assert payload["execution_authorized"] is False


@pytest.mark.parametrize(
    ("changes", "route", "reason"),
    [
        ({"state": "closed", "risk_flags": ["security"]}, "ignore", "closed_or_out_of_scope"),
        ({"in_scope": False, "maintainer_welcome": False}, "ignore", "closed_or_out_of_scope"),
        (
            {"risk_flags": ["security"], "maintainer_welcome": False},
            "design",
            "risk_requires_human_design",
        ),
        (
            {"maintainer_welcome": False, "complexity": "unknown"},
            "design",
            "maintainer_coordination_required",
        ),
        (
            {"kind": "feature", "requirements_clear": False},
            "design",
            "scope_requires_design",
        ),
        (
            {"complexity": "medium", "requirements_clear": False},
            "design",
            "scope_requires_design",
        ),
        (
            {"complexity": "unknown", "reproducer_present": False},
            "research",
            "insufficient_requirements",
        ),
        (
            {"requirements_clear": False, "tests_available": False},
            "research",
            "insufficient_requirements",
        ),
        (
            {"reproducer_present": False, "tests_available": False},
            "research",
            "reproducer_required",
        ),
        ({"tests_available": False}, "research", "verification_required"),
    ],
)
def test_routing_precedence(
    tmp_path: Path, changes: dict[str, object], route: str, reason: str
) -> None:
    result = run_cli("triage", write_json(tmp_path, {**BASE_FACTS, **changes}))

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert (payload["route"], payload["reason"]) == (route, reason)
    assert payload["execution_authorized"] is False


@pytest.mark.parametrize(
    "field",
    [
        "in_scope",
        "requirements_clear",
        "reproducer_present",
        "tests_available",
        "maintainer_welcome",
    ],
)
def test_nontruthy_values_are_not_accepted_as_booleans(tmp_path: Path, field: str) -> None:
    assert_invalid(run_cli("triage", write_json(tmp_path, {**BASE_FACTS, field: 0})))


@pytest.mark.parametrize(
    "value",
    [
        {**BASE_FACTS, "schema_version": 2},
        {**BASE_FACTS, "schema_version": False},
        {key: value for key, value in BASE_FACTS.items() if key != "kind"},
        {**BASE_FACTS, "unknown": True},
        {**BASE_FACTS, "risk_flags": "security"},
        {**BASE_FACTS, "risk_flags": [["security"]]},
        [BASE_FACTS],
    ],
)
def test_schema_unknown_fields_and_nested_types_are_rejected(tmp_path: Path, value: object) -> None:
    assert_invalid(run_cli("triage", write_json(tmp_path, value)))


@pytest.mark.parametrize(
    "raw",
    [
        "{not json",
        '{"schema_version": 1, "schema_version": 1}',
        "[" * 1100 + "]" * 1100,
    ],
)
def test_malformed_duplicate_and_deeply_nested_json_are_safe(tmp_path: Path, raw: str) -> None:
    secret = "private-household-value"
    path = tmp_path / secret
    path.write_text(raw, encoding="utf-8")

    assert_invalid(run_cli("triage", path), secret)


def test_missing_file_uses_safe_read_error(tmp_path: Path) -> None:
    result = run_cli("triage", tmp_path / "private-household-value.json")

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: cannot read input file\n"
    assert "private-household-value" not in result.stderr


@pytest.mark.parametrize(
    "arguments",
    [
        (),
        ("private-command-value", "input.json"),
        ("triage", "input.json", "private-extra-value"),
    ],
)
def test_argument_errors_do_not_echo_user_values(arguments: tuple[str, ...]) -> None:
    result = run_cli_args(*arguments)

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == (
        "usage: chimken-lab [-h] {triage,evaluate} input\nchimken-lab: error: invalid arguments\n"
    )
    assert "private-" not in result.stderr


def test_repository_eval_fixture_reports_metadata_and_passes() -> None:
    fixture = REPO_ROOT / "evals" / "oss-triage.json"

    result = run_cli("evaluate", fixture)

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    assert payload["runner_version"] == "0.1.0"
    assert payload["python_version"] == platform.python_version()
    assert payload["policy_version"] == "oss-triage-rules-v1"
    assert payload["dataset_sha256"] == hashlib.sha256(fixture.read_bytes()).hexdigest()
    assert payload["passed"] is True
    assert payload["execution_authorized"] is False
    assert payload["metrics"]["total"] == len(payload["cases"])
    assert payload["metrics"]["correct"] == len(payload["cases"])
    assert payload["metrics"]["accuracy"] == 1.0
    assert payload["metrics"]["false_agent_candidates"] == 0
    assert payload["metrics"]["model_calls"] == 0
    assert payload["metrics"]["model_cost_usd"] == 0
    assert isinstance(payload["metrics"]["elapsed_seconds"], float)


def test_wrong_expected_outcome_exits_one_and_records_mismatch(tmp_path: Path) -> None:
    suite = {
        "schema_version": 1,
        "cases": [{"id": "wrong-route", "facts": BASE_FACTS, "expected": "research"}],
    }

    result = run_cli("evaluate", write_json(tmp_path, suite))

    assert result.returncode == 1
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["passed"] is False
    assert payload["execution_authorized"] is False
    assert payload["metrics"]["correct"] == 0
    assert payload["metrics"]["accuracy"] == 0.0
    assert payload["metrics"]["false_agent_candidates"] == 1
    assert payload["cases"] == [
        {
            "actual": "agent_candidate",
            "expected": "research",
            "id": "wrong-route",
            "passed": False,
            "reason": "bounded_candidate_pending_authorization",
        }
    ]


@pytest.mark.parametrize(
    "cases",
    [
        [],
        [{"id": "", "facts": BASE_FACTS, "expected": "agent_candidate"}],
        [
            {"id": "duplicate", "facts": BASE_FACTS, "expected": "agent_candidate"},
            {"id": "duplicate", "facts": BASE_FACTS, "expected": "agent_candidate"},
        ],
    ],
)
def test_empty_suite_and_empty_or_duplicate_ids_are_invalid(
    tmp_path: Path, cases: list[dict[str, object]]
) -> None:
    suite = {"schema_version": 1, "cases": cases}

    assert_invalid(run_cli("evaluate", write_json(tmp_path, suite)))


@pytest.mark.parametrize(
    "suite",
    [
        {"schema_version": 1, "cases": [], "unknown": True},
        {"schema_version": "1", "cases": []},
        {"schema_version": 1, "cases": {}},
        {
            "schema_version": 1,
            "cases": [{"id": "case", "facts": BASE_FACTS, "expected": "execute"}],
        },
        {
            "schema_version": 1,
            "cases": [
                {
                    "id": "case",
                    "facts": BASE_FACTS,
                    "expected": "agent_candidate",
                    "unknown": True,
                }
            ],
        },
    ],
)
def test_eval_schema_and_unknown_fields_are_rejected(tmp_path: Path, suite: object) -> None:
    assert_invalid(run_cli("evaluate", write_json(tmp_path, suite)))
