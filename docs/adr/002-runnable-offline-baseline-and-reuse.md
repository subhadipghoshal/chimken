# ADR 002: Runnable offline baseline and reuse

Status: accepted

The first slice is a Python 3.12+ `uv` workspace with a pure policy package and an offline CLI. It reuses standard Python tooling and has no provider, cloud, or framework dependency. We will experiment before adopting frameworks and add infrastructure only after a workload demonstrates a need. This gives future automation a cheap, reproducible baseline.

Tradeoff: the deterministic policy establishes interfaces and regression behavior, but does not evaluate live issue understanding or prove autonomous fix quality. Shared workspace dependencies simplify two cooperating packages; experiments with conflicting environments remain independent.

Revisit once an existing tool has been exercised against the same fixture and acceptance criteria, and its integration benefit exceeds its maintenance and operating cost. Record that evidence before adopting a framework or adding a service.
