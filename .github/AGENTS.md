# GitHub automation guidance

- Keep workflows unprivileged. Use `pull_request`, never `pull_request_target`.
- Set the smallest practical `permissions` block and do not expose secrets to pull requests.
- Pin third-party GitHub Actions to full commit SHAs. Keep action updates in Dependabot pull requests.
- CI must remain deterministic, run with `--locked`, use timeouts, and avoid deployment or repository-writing steps.
- Issue and pull request templates are public-facing. Ask contributors not to include private or sensitive data.
