# Agent guidance

Read this file before work. Keep changes small, observable, and within the assigned scope. Prefer existing tools and a measured experiment before adding a framework.

- Use an isolated Git worktree for concurrent writers. State the exact file scope and obtain independent review before publication.
- GitHub Issues are the canonical tasks. The project board may organize them.
- Treat issue triage as recommendation only. Respect explicit task authorization. Seek human direction for new costly, private, destructive, or externally visible actions beyond that scope.
- Keep private household data, credentials, runtime state, and external clones outside Git. Sanitize and verify sources before public upload.
- This repository is public and stays public (ADR 004). Sensitive information lives in the data layer (GitHub Projects, Notion, Google Drive, host filesystem and databases), never in commits, issues, PRs or logs. Operations config uses placeholders resolved from the data layer at deploy time.
- Keep dependencies directional: apps may import capability packages. Do not create a generic shared package for one use.

Run the documented checks in `CONTRIBUTING.md` for the area you change.
