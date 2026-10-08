# Security

Report vulnerabilities privately through [GitHub Security Advisories](https://github.com/subhadipghoshal/chimken/security/advisories/new). Private vulnerability reporting is enabled. Do not include secrets or sensitive personal data in public issues.

The project is an experimental pre-release. Security fixes target the current default branch; no older release line is maintained yet.

## Current boundaries

- The lab reads an explicitly selected local JSON file, validates it, and writes a JSON report to stdout. It does not execute commands from input, call providers, or authorize actions.
- Issue text, retrieved documents, tool output, and model assessments are untrusted data. Future integrations must keep those separate from instructions and credentials.
- Household data, credentials, runtime state, traces, databases, and external OSS clones belong outside the public checkout. Use synthetic fixtures and inspect the staged diff before publishing.
- Repository checks catch prohibited paths and artifact types. They are not a complete detector of secrets or personal data. GitHub secret scanning and push protection supplement human review.
- CI runs with read-only repository permissions, pinned actions, no persisted checkout credentials, and no household or provider secrets.

If a credential is exposed, revoke or rotate it first and report privately. Removing a file from the latest commit does not remove it from Git history.
