# Apps guidance

Apps are user-facing entry points. Keep them thin and depend only on the capability packages they need. `chimken-lab` is an offline CLI and must keep stdout machine-readable. Do not add provider calls, background watchers, or state storage without a demonstrated workload and explicit approval.
