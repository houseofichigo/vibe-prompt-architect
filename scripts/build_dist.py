#!/usr/bin/env python3
"""Rebuild dist/skill.zip from skills/<name>/ (byte-reproducible).

Usage:
    python3 scripts/build_dist.py          # rebuild the ZIP
    python3 scripts/build_dist.py --check  # exit 1 if the ZIP is out of date
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import skill_rules as sr  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only report whether dist/skill.zip is up to date")
    args = ap.parse_args(argv)
    skill_root, roots = sr.find_repo_skill(ROOT)
    if skill_root is None:
        print(f"Expected exactly one skills/<name>/SKILL.md, found {len(roots)}", file=sys.stderr)
        return 2
    out = ROOT / "dist" / "skill.zip"
    if args.check:
        diffs = sr.compare_zip(skill_root, out, skill_root.name)
        if diffs:
            print("dist/skill.zip is out of date:")
            print("\n".join("- " + d for d in diffs))
            print("Run: python3 scripts/build_dist.py")
            return 1
        print("dist/skill.zip is up to date")
        return 0
    files = sr.build_zip(skill_root, out, skill_root.name)
    print(f"Wrote {out.relative_to(ROOT)} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
