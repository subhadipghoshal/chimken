from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
DOMAIN_ROOT = REPO_ROOT / "packages" / "oss-triage" / "src" / "chimken_oss_triage"
FORBIDDEN_IMPORTS = {"chimken_lab", "evals", "experiments", "workflows"}


def test_domain_package_does_not_depend_on_outer_layers() -> None:
    violations: list[str] = []
    for source_path in DOMAIN_ROOT.rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            imported_roots: set[str] = set()
            if isinstance(node, ast.Import):
                imported_roots = {alias.name.partition(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots = {node.module.partition(".")[0]}
            for imported_root in imported_roots & FORBIDDEN_IMPORTS:
                violations.append(f"{source_path.relative_to(REPO_ROOT)} imports {imported_root}")

    assert violations == []
