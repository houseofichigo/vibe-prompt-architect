#!/usr/bin/env python3
"""Validate the Agent Skill in this repository.

Checks the Skill at skills/<name>/ against the open Agent Skills spec plus the
Claude and OpenAI/Codex rules, and confirms dist/skill.zip matches the Skill
folder exactly. Standard library only.

Usage:
    python3 scripts/validate_skill.py [--target all|portable|claude|openai] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import skill_rules as sr  # noqa: E402

# Host rules this repository promises to satisfy (set when the repo was generated).
DEFAULT_TARGET = "all"


def run(target: str = DEFAULT_TARGET) -> dict:
    findings = []
    skill_root, roots = sr.find_repo_skill(ROOT)
    if skill_root is None:
        findings.append(("blocker", "skill_count", f"Expected exactly one skills/<name>/SKILL.md, found {len(roots)}", "skills/"))
        return {"status": "fail", "skill": None, "findings": findings}
    fields, rule_findings = sr.validate_skill_dir(skill_root, target)
    findings += rule_findings
    name = skill_root.name
    for diff in sr.compare_zip(skill_root, ROOT / "dist" / "skill.zip", name):
        findings.append(("blocker", "dist_out_of_sync", diff + " (run: python3 scripts/build_dist.py)", "dist/skill.zip"))
    if not any((ROOT / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
        findings.append(("warning", "no_repo_license", "No LICENSE file: others cannot legally reuse this Skill", "LICENSE"))
    status = "fail" if any(f[0] == "blocker" for f in findings) else "pass"
    return {"status": status, "skill": name, "target": sr.normalize_target(target), "findings": findings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default=DEFAULT_TARGET, help=f"all, portable, claude, or openai (default: {DEFAULT_TARGET})")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        sr.normalize_target(args.target)
    except ValueError as e:
        ap.error(str(e))
    result = run(args.target)
    if args.json:
        out = dict(result)
        out["findings"] = [dict(zip(("severity", "code", "message", "path"), f)) for f in result["findings"]]
        print(json.dumps(out, indent=2))
    else:
        print(f"{result['status'].upper()}: skills/{result['skill'] or '?'} (target: {result.get('target', args.target)})")
        if result["findings"]:
            print(sr.format_findings(result["findings"]))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
