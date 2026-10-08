# OSS contribution workflow

`example.json` is a local, manually assessed facts record for the offline triage policy. Run it with:

```sh
uv run --all-packages --locked chimken-lab triage workflows/oss-contributions/example.json
```

The result is a recommendation, never authorization. An `agent_candidate` route still requires a human to approve any external action. Use GitHub Issues as the canonical task record and retain human control of communications, pull requests, paid services, private data, and other external effects.
