from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manifest_utils import (
    apply_generated_block,
    find_const_files,
    find_package_dir,
    load_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the plugin.json-derived metadata block in const.py."
    )
    parser.add_argument("--repo", default=".", help="Plugin repository root.")
    parser.add_argument("--check", action="store_true", help="Compare only.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    package_dir = find_package_dir(repo)
    manifest = load_json(package_dir / "plugin.json")
    const_files = find_const_files(package_dir)
    if len(const_files) != 1:
        raise ValueError(f"expected exactly one const file in {package_dir}, found {len(const_files)}")
    path = const_files[0]
    display = path.relative_to(repo).as_posix()

    current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    expected = apply_generated_block(current, manifest)
    if current == expected:
        print(f"PASS const {display}")
        return 0
    if args.check:
        print(f"FAIL CONST_OUTDATED {display}")
        return 1
    path.write_text(expected, encoding="utf-8", newline="\n")
    print(f"PASS const generated {display}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL SCRIPT_ERROR {exc}", file=sys.stderr)
        raise SystemExit(2)
