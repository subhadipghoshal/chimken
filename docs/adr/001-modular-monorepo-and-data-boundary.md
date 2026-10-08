# ADR 001: Modular monorepo and data boundary

Status: accepted

Chimken groups code by capability and keeps dependencies one directional. The lab imports the OSS-triage policy; a generic shared package is not justified. Git holds public source and architecture, while private household data, secrets, runtime state, and external clones remain outside Git. This preserves a small, auditable public core and avoids turning source control into a runtime database.

Tradeoff: cross-capability changes are easier to coordinate, but a monorepo shares repository visibility and makes accidental coupling easier. Package boundaries and public-data checks reduce that risk; they do not isolate permissions within Git.

Revisit when a component needs separate visibility, ownership, release cadence, or when repository operations become measurably burdensome. Size or a different programming language alone is not a split trigger.
