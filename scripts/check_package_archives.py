"""Verify that built package archives contain the repository Apache license."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import NoReturn

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> NoReturn:
    raise SystemExit(f"error: {message}")


def check_members(archive: Path, members: dict[str, bytes], expected_license: bytes) -> None:
    license_members = {
        name: contents
        for name, contents in members.items()
        if PurePosixPath(name).name == "LICENSE"
    }
    if len(license_members) != 1:
        fail(f"{archive}: expected exactly one LICENSE member, found {len(license_members)}")
    member_name, contents = next(iter(license_members.items()))
    if contents != expected_license:
        fail(f"{archive}: {member_name} does not match the repository LICENSE")


def check_wheel(archive: Path, expected_license: bytes) -> None:
    with zipfile.ZipFile(archive) as wheel:
        check_members(
            archive, {name: wheel.read(name) for name in wheel.namelist()}, expected_license
        )


def check_sdist(archive: Path, expected_license: bytes) -> None:
    with tarfile.open(archive, "r:gz") as sdist:
        members: dict[str, bytes] = {}
        for member in sdist.getmembers():
            if member.isfile():
                file_object = sdist.extractfile(member)
                if file_object is None:
                    fail(f"{archive}: could not read {member.name}")
                members[member.name] = file_object.read()
        check_members(archive, members, expected_license)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    arguments = parser.parse_args()
    expected_license = (REPOSITORY_ROOT / "LICENSE").read_bytes()

    for archive in arguments.archives:
        if archive.suffix == ".whl":
            check_wheel(archive, expected_license)
        elif archive.name.endswith(".tar.gz"):
            check_sdist(archive, expected_license)
        else:
            fail(f"{archive}: expected a wheel or .tar.gz sdist")


if __name__ == "__main__":
    main()
