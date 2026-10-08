# Packages guidance

Packages own narrow capabilities. `chimken-oss-triage` is pure and deterministic: no I/O, network access, model calls, or authorization. Preserve its clear input validation and one-way dependency boundary from app to package.
