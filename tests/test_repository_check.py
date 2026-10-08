from __future__ import annotations

import os
import subprocess
from pathlib import Path

from scripts.check_repository import check_repository

REPO_ROOT = Path(__file__).parents[1]


def git(repo: Path, *args: str) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_EMAIL": "tests@example.invalid",
            "GIT_AUTHOR_NAME": "Chimken Tests",
            "GIT_COMMITTER_EMAIL": "tests@example.invalid",
            "GIT_COMMITTER_NAME": "Chimken Tests",
        }
    )
    completed = subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def initialize_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "public-repo"
    repo.mkdir()
    git(repo, "init", "--quiet")
    (repo / ".gitignore").write_text("private/\n*.key\n", encoding="utf-8")
    (repo / "README.md").write_text("# Public project\n", encoding="utf-8")
    git(repo, "add", ".gitignore", "README.md")
    git(repo, "commit", "--quiet", "-m", "initial public files")
    return repo


def test_checker_accepts_a_clean_public_repository(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    (repo / "new.py").write_text("print('public')\n", encoding="utf-8")
    (repo / "odd\tname\n-.txt").write_text("unusual filename\n", encoding="utf-8")

    assert check_repository(repo) == []


def test_checker_rejects_force_added_private_file_without_reading_it(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    private_file = repo / "private" / "credentials.json"
    private_file.parent.mkdir()
    private_file.write_text("unique-secret-that-must-not-be-reported\n", encoding="utf-8")
    git(repo, "add", "--force", "private/credentials.json")

    violations = check_repository(repo)

    assert {violation.path for violation in violations} == {"private/credentials.json"}
    assert {violation.reason for violation in violations} == {
        "private or runtime path",
        "tracked file is ignored",
    }
    assert "unique-secret-that-must-not-be-reported" not in repr(violations)


def test_checker_rejects_a_gitlink(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    commit = git(repo, "rev-parse", "HEAD")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{commit},vendor/dependency")

    violations = check_repository(repo)

    assert [(violation.path, violation.reason) for violation in violations] == [
        ("vendor/dependency", "gitlink")
    ]


def test_checker_rejects_untracked_symlink_sensitive_names_and_large_files(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    (repo / "target.txt").write_text("target\n", encoding="utf-8")
    (repo / "shortcut").symlink_to("target.txt")
    (repo / "service.log").write_text("log\n", encoding="utf-8")
    (repo / "large.bin").write_bytes(b"x" * 1_048_577)

    violations = check_repository(repo)

    assert {(violation.path, violation.reason) for violation in violations} == {
        ("large.bin", "artifact exceeds 1 MiB"),
        ("service.log", "credential, key, database, log, or state artifact"),
        ("shortcut", "symbolic link"),
    }


def test_checker_cli_exit_codes_zero_and_one(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    clean = subprocess.run(
        [os.fspath(Path(os.sys.executable)), os.fspath(REPO_ROOT / "scripts/check_repository.py")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    (repo / "state").mkdir()
    (repo / "state" / "run.txt").write_text("runtime data\n", encoding="utf-8")
    dirty = subprocess.run(
        [os.fspath(Path(os.sys.executable)), os.fspath(REPO_ROOT / "scripts/check_repository.py")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert (clean.returncode, clean.stdout, clean.stderr) == (0, "", "")
    assert dirty.returncode == 1
    assert dirty.stdout == ""
    assert dirty.stderr == "private or runtime path: state/run.txt\n"
