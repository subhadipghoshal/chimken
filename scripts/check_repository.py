"""Reject files that do not belong in Chimken's public source repository."""

from __future__ import annotations

import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_ARTIFACT_BYTES = 1_048_576

PRIVATE_PATH_PARTS = frozenset(
    {
        "artifacts",
        "clone",
        "clones",
        "data",
        "external",
        "household",
        "logs",
        "private",
        "runs",
        "secrets",
        "state",
        "worktree",
        "worktrees",
        ".worktrees",
    }
)

SENSITIVE_NAME_PATTERNS = (
    re.compile(r"^\.env(?:\..+)?$", re.IGNORECASE),
    re.compile(r"^credentials?(?:[._-].*)?$", re.IGNORECASE),
    re.compile(r"^(?:id_)?(?:rsa|dsa|ecdsa|ed25519)(?:\.pub)?$", re.IGNORECASE),
    re.compile(r".+\.(?:pem|key|p12|pfx)$", re.IGNORECASE),
    re.compile(r".+\.(?:db|sqlite|sqlite3|jsonl|tfvars)$", re.IGNORECASE),
    re.compile(r".+\.log(?:\..+)?$", re.IGNORECASE),
    re.compile(r".+\.db-.+$", re.IGNORECASE),
    re.compile(r".+\.sqlite.+$", re.IGNORECASE),
    re.compile(r".+\.tfstate(?:\..+)?$", re.IGNORECASE),
)


@dataclass(frozen=True, order=True)
class Violation:
    path: str
    reason: str


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("git repository inspection failed")
    return completed.stdout


def _paths(output: bytes) -> list[str]:
    return [os.fsdecode(value) for value in output.split(b"\0") if value]


def _staged_entries(repo: Path) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    for record in _git(repo, "ls-files", "-z", "--stage").split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_id, _stage = metadata.decode("ascii").split()
        entries[os.fsdecode(raw_path)] = (mode, object_id)
    return entries


def _blob_sizes(repo: Path, object_ids: set[str]) -> dict[str, int]:
    usable_ids = sorted(object_id for object_id in object_ids if set(object_id) != {"0"})
    if not usable_ids:
        return {}
    output = _git(
        repo,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        input_bytes=("\n".join(usable_ids) + "\n").encode("ascii"),
    )
    sizes: dict[str, int] = {}
    for line in output.decode("ascii").splitlines():
        object_id, object_type, size = line.split()
        if object_type == "blob":
            sizes[object_id] = int(size)
    return sizes


def _path_reason(path: str) -> str | None:
    parts = Path(path).parts
    if any(part.casefold() in PRIVATE_PATH_PARTS for part in parts):
        return "private or runtime path"
    if SENSITIVE_NAME_PATTERNS and any(
        pattern.fullmatch(parts[-1]) for pattern in SENSITIVE_NAME_PATTERNS
    ):
        return "credential, key, database, log, or state artifact"
    return None


def check_repository(repo_path: str | Path) -> list[Violation]:
    """Return public-repository policy violations without reading file contents."""
    repo = Path(repo_path).resolve()
    top_level = Path(os.fsdecode(_git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
    if top_level != repo:
        raise ValueError("repo_path must be the repository root")

    all_paths = _paths(_git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard"))
    ignored_tracked = set(
        _paths(_git(repo, "ls-files", "-z", "--cached", "--ignored", "--exclude-standard"))
    )
    staged = _staged_entries(repo)
    blob_sizes = _blob_sizes(repo, {object_id for _mode, object_id in staged.values()})
    violations: set[Violation] = set()

    for path in all_paths:
        if path in ignored_tracked:
            violations.add(Violation(path, "tracked file is ignored"))

        reason = _path_reason(path)
        if reason:
            violations.add(Violation(path, reason))

        entry = staged.get(path)
        if entry:
            mode, object_id = entry
            if mode == "120000":
                violations.add(Violation(path, "symbolic link"))
            elif mode == "160000":
                violations.add(Violation(path, "gitlink"))
            if blob_sizes.get(object_id, 0) > MAX_ARTIFACT_BYTES:
                violations.add(Violation(path, "artifact exceeds 1 MiB"))

        working_path = repo / path
        try:
            metadata = working_path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode):
            violations.add(Violation(path, "symbolic link"))
        elif stat.S_ISREG(metadata.st_mode) and metadata.st_size > MAX_ARTIFACT_BYTES:
            violations.add(Violation(path, "artifact exceeds 1 MiB"))

    return sorted(violations)


def main() -> int:
    try:
        violations = check_repository(Path.cwd())
    except (OSError, RuntimeError, ValueError):
        print("error: repository inspection failed", file=sys.stderr)
        return 2
    for violation in violations:
        print(f"{violation.reason}: {violation.path}", file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
