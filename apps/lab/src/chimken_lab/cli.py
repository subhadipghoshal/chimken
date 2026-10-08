"""Load explicit local inputs, run pure recommendations, and print aggregate evidence."""

import argparse
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from time import perf_counter
from typing import NoReturn

from chimken_oss_triage import POLICY_VERSION, IssueFacts, Route, recommend

from chimken_lab import __version__

MAX_INPUT_BYTES = 1_048_576
_SUITE_FIELDS = frozenset({"schema_version", "cases"})
_CASE_FIELDS = frozenset({"id", "facts", "expected"})


class _SafeArgumentParser(argparse.ArgumentParser):
    """Report invalid arguments without reflecting user-provided values."""

    def error(self, _message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: invalid arguments\n")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _load(path: Path) -> tuple[object, str]:
    with path.open("rb") as source:
        raw = source.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 1 MiB")
    value = json.loads(raw, object_pairs_hook=_unique_object)
    return value, hashlib.sha256(raw).hexdigest()


def evaluate(value: object, dataset_sha256: str) -> dict[str, object]:
    """Evaluate a bounded synthetic suite; a mismatch fails the command."""
    if not isinstance(value, dict) or set(value) != _SUITE_FIELDS:
        raise ValueError("suite requires schema_version and cases")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported suite schema_version")
    cases = value["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
        raise ValueError("suite requires 1 to 1000 cases")
    seen: set[str] = set()
    results: list[dict[str, object]] = []
    correct = 0
    false_candidates = 0
    started = perf_counter()
    for case in cases:
        if not isinstance(case, dict) or set(case) != _CASE_FIELDS:
            raise ValueError("case requires id, facts, and expected")
        case_id = case["id"]
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]{1,80}", case_id):
            raise ValueError("case id must be a short lowercase slug")
        if case_id in seen:
            raise ValueError("case ids must be unique")
        seen.add(case_id)
        expected = case["expected"]
        if not isinstance(expected, str) or expected not in Route:
            raise ValueError("invalid expected route")
        decision = recommend(IssueFacts.from_dict(case["facts"]))
        passed = decision.route == expected
        correct += passed
        false_candidates += decision.route == Route.AGENT_CANDIDATE and not passed
        results.append(
            {
                "id": case_id,
                "expected": expected,
                "actual": decision.route,
                "reason": decision.reason,
                "passed": passed,
            }
        )
    return {
        "schema_version": 1,
        "runner_version": __version__,
        "python_version": platform.python_version(),
        "policy_version": POLICY_VERSION,
        "dataset_sha256": dataset_sha256,
        "cases": results,
        "metrics": {
            "total": len(cases),
            "correct": correct,
            "accuracy": correct / len(cases),
            "false_agent_candidates": false_candidates,
            "elapsed_seconds": round(perf_counter() - started, 6),
            "model_calls": 0,
            "model_cost_usd": 0,
        },
        "passed": correct == len(cases),
        "execution_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = _SafeArgumentParser(
        prog="chimken-lab", description="Offline Chimken triage and evaluation lab"
    )
    parser.add_argument("command", choices=["triage", "evaluate"])
    parser.add_argument("input", type=Path, help="explicit local JSON file (maximum 1 MiB)")
    args = parser.parse_args(argv)
    try:
        value, digest = _load(args.input)
        if args.command == "triage":
            decision = recommend(IssueFacts.from_dict(value))
            result: dict[str, object] = {
                "schema_version": 1,
                "policy_version": POLICY_VERSION,
                "route": decision.route,
                "reason": decision.reason,
                "execution_authorized": False,
            }
        else:
            result = evaluate(value, digest)
    except OSError:
        print("error: cannot read input file", file=sys.stderr)
        return 2
    except (ValueError, UnicodeError, RecursionError):
        # Do not reflect potentially private input values into logs.
        print("error: invalid input; see docs/contracts/oss-triage.md", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 1 if result.get("passed") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
