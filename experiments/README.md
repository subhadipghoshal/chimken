# Experiments

An experiment earns complexity only when it records an operational lesson. Create a short note using this template:

```text
Hypothesis:
Baseline:
Method:
Budget: local compute, money, human time, and trial count
Success measure:
Ground feedback:
Promote or stop decision:
```

## Initial experiment: offline OSS triage

Hypothesis: a deterministic policy can provide a cheap, inspectable baseline for deciding whether an OSS item needs research, design, or a bounded agent candidate.

Baseline: manual review. Method: run the 18 synthetic cases in `evals/oss-triage.json`; inspect the routes and reasons. Budget: local compute only. Success: all cases pass and routes and reasons remain deterministic (elapsed time varies). Ground feedback: compare recommendations with reviewed operational outcomes before changing the policy. Promote only if that feedback justifies another capability; otherwise stop or refine the fixture.
