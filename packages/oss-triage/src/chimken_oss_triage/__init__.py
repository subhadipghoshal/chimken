"""Public triage interface. Recommendations never grant execution authority."""

from .policy import POLICY_VERSION, Decision, IssueFacts, Route, recommend

__all__ = ["POLICY_VERSION", "Decision", "IssueFacts", "Route", "recommend"]
