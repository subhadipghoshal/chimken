# Evaluations

`oss-triage.json` is an 18-case synthetic regression suite for the offline policy. Run it with:

```sh
uv run --all-packages --locked chimken-lab evaluate evals/oss-triage.json
```

The result records the dataset hash, per-case route, aggregate accuracy, elapsed local time, and zero model calls and cost. It is a regression check, not evidence that models or agents are generally capable.

For future experiments, repeat trials and report separate dimensions:

- deterministic correctness: repeatable behavior for the same input;
- artifact quality: the produced code, document, or other deliverable;
- trajectory quality: decisions and recovery during the run;
- operational quality: time, cost, reliability, and operator burden;
- outcome quality: whether the intended real-world result occurred.

Evaluate the whole model, harness, tools, and context together. Do not infer capability from model stereotypes.
