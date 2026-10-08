"""A cheap baseline to measure before adopting a model or orchestration framework."""

from dataclasses import dataclass
from enum import StrEnum

POLICY_VERSION = "oss-triage-rules-v1"
RISK_FLAGS = frozenset(
    {
        "security",
        "credentials",
        "personal_data",
        "breaking_change",
        "dependencies",
        "infrastructure",
        "unclear_ownership",
    }
)
_ISSUE_FACT_FIELDS = frozenset(
    {
        "schema_version",
        "state",
        "kind",
        "complexity",
        "in_scope",
        "requirements_clear",
        "reproducer_present",
        "tests_available",
        "maintainer_welcome",
        "risk_flags",
    }
)


class Route(StrEnum):
    IGNORE = "ignore"
    RESEARCH = "research"
    DESIGN = "design"
    AGENT_CANDIDATE = "agent_candidate"


@dataclass(frozen=True)
class IssueFacts:
    """Manually assessed facts, not issue text or model-granted permissions."""

    state: str
    kind: str
    complexity: str
    in_scope: bool
    requirements_clear: bool
    reproducer_present: bool
    tests_available: bool
    maintainer_welcome: bool
    risk_flags: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.state, str) or self.state not in {"open", "closed"}:
            raise ValueError("invalid state")
        if not isinstance(self.kind, str) or self.kind not in {"docs", "bug", "feature"}:
            raise ValueError("invalid kind")
        if not isinstance(self.complexity, str) or self.complexity not in {
            "small",
            "medium",
            "large",
            "unknown",
        }:
            raise ValueError("invalid complexity")
        for name, value in (
            ("in_scope", self.in_scope),
            ("requirements_clear", self.requirements_clear),
            ("reproducer_present", self.reproducer_present),
            ("tests_available", self.tests_available),
            ("maintainer_welcome", self.maintainer_welcome),
        ):
            if type(value) is not bool:
                raise ValueError(f"{name} must be boolean")
        if not isinstance(self.risk_flags, tuple) or any(
            not isinstance(flag, str) or flag not in RISK_FLAGS for flag in self.risk_flags
        ):
            raise ValueError("invalid risk_flags")

    @classmethod
    def from_dict(cls, value: object) -> "IssueFacts":
        if not isinstance(value, dict) or set(value) != _ISSUE_FACT_FIELDS:
            raise ValueError("issue facts require exactly the documented fields")
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("unsupported issue facts schema_version")

        state = value["state"]
        kind = value["kind"]
        complexity = value["complexity"]
        in_scope = value["in_scope"]
        requirements_clear = value["requirements_clear"]
        reproducer_present = value["reproducer_present"]
        tests_available = value["tests_available"]
        maintainer_welcome = value["maintainer_welcome"]
        risk_flags = value["risk_flags"]

        if not isinstance(state, str):
            raise ValueError("state must be a string")
        if not isinstance(kind, str):
            raise ValueError("kind must be a string")
        if not isinstance(complexity, str):
            raise ValueError("complexity must be a string")
        if type(in_scope) is not bool:
            raise ValueError("in_scope must be boolean")
        if type(requirements_clear) is not bool:
            raise ValueError("requirements_clear must be boolean")
        if type(reproducer_present) is not bool:
            raise ValueError("reproducer_present must be boolean")
        if type(tests_available) is not bool:
            raise ValueError("tests_available must be boolean")
        if type(maintainer_welcome) is not bool:
            raise ValueError("maintainer_welcome must be boolean")
        if not isinstance(risk_flags, list) or any(
            not isinstance(flag, str) for flag in risk_flags
        ):
            raise ValueError("risk_flags must be a list")

        return cls(
            state=state,
            kind=kind,
            complexity=complexity,
            in_scope=in_scope,
            requirements_clear=requirements_clear,
            reproducer_present=reproducer_present,
            tests_available=tests_available,
            maintainer_welcome=maintainer_welcome,
            risk_flags=tuple(risk_flags),
        )


@dataclass(frozen=True)
class Decision:
    route: Route
    reason: str


def recommend(facts: IssueFacts) -> Decision:
    """Suggest a next step. This function performs no I/O and authorizes no action."""
    if facts.state == "closed" or not facts.in_scope:
        return Decision(Route.IGNORE, "closed_or_out_of_scope")
    if facts.risk_flags:
        return Decision(Route.DESIGN, "risk_requires_human_design")
    if not facts.maintainer_welcome:
        return Decision(Route.DESIGN, "maintainer_coordination_required")
    if facts.kind == "feature" or facts.complexity in {"medium", "large"}:
        return Decision(Route.DESIGN, "scope_requires_design")
    if facts.complexity == "unknown" or not facts.requirements_clear:
        return Decision(Route.RESEARCH, "insufficient_requirements")
    if facts.kind == "bug" and not facts.reproducer_present:
        return Decision(Route.RESEARCH, "reproducer_required")
    if not facts.tests_available:
        return Decision(Route.RESEARCH, "verification_required")
    return Decision(Route.AGENT_CANDIDATE, "bounded_candidate_pending_authorization")
