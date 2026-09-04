#!/usr/bin/env python3
"""
Hermes Agent -> SOCIS Agent rebrand executor.

Usage:
    python run_rebrand.py --root . --report out.json          # dry run
    python run_rebrand.py --root . --apply-text                 # rewrite file contents
    python run_rebrand.py --root . --apply-renames               # rename files/dirs
    python run_rebrand.py --root . --apply-text --apply-renames  # both (recommended order)

Design:
  - DRY RUN IS THE DEFAULT.
  - Writes a JSON report of every file touched / renamed for review.
  - EXCLUDE_PATHS protects binaries, git internals, contributor personal
    data, LICENSE/NOTICE files anywhere in the tree, and this script's
    own directory.
  - Text substitution runs in a fixed tier order (domains -> home-dir path
    forms -> env prefix -> module names -> general prose) so specific
    identifiers always beat the generic bare "hermes"->"socis" rule.
  - Extensionless files (shebang scripts, s6 service files, Dockerfiles)
    ARE included in the text pass - a renamed-but-not-rewritten CLI
    wrapper was a real bug found during development.
  - Renames run in two passes: curated MODULE_RENAMES first, then a
    generic bottom-up sweep that renames every remaining file/dir whose
    NAME matches the same replacement table, so nothing is missed.
  - Post-flight: syntax-checks every .py file and checks for stale
    module-name imports. A clean replacement count alone is not proof of
    correctness - review the diff before committing.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rebrand_map import (
    ENV_PREFIX_OLD, ENV_PREFIX_NEW,
    HOME_DIR_PATH_FORMS,
    MODULE_NAME_TEXT_REPLACEMENTS,
    PROSE_REPLACEMENTS, DOMAIN_REPLACEMENTS,
    MODULE_RENAMES, EXCLUDE_PATHS, TEXT_EXTENSIONS,
    EXTENSIONLESS_LICENSE_NAMES,
)


def is_excluded(path: str) -> bool:
    return any(ex in path for ex in EXCLUDE_PATHS)


def is_text_candidate(fname: str) -> bool:
    if fname in EXTENSIONLESS_LICENSE_NAMES:
        return False
    ext = os.path.splitext(fname)[1]
    if ext in TEXT_EXTENSIONS:
        return True
    if ext == "":
        return True
    return False


def build_replacement_table():
    tier1 = sorted(DOMAIN_REPLACEMENTS, key=lambda p: -len(p[0]))
    tier2 = sorted(HOME_DIR_PATH_FORMS, key=lambda p: -len(p[0]))
    tier3 = [(ENV_PREFIX_OLD, ENV_PREFIX_NEW)]
    tier4 = sorted(MODULE_NAME_TEXT_REPLACEMENTS, key=lambda p: -len(p[0]))
    tier5 = sorted(PROSE_REPLACEMENTS, key=lambda p: -len(p[0]))
    return tier1 + tier2 + tier3 + tier4 + tier5


def apply_text_replacements(content: str, table) -> tuple:
    counts = {}
    for old, new in table:
        if old in content:
            counts[old] = content.count(old)
            content = content.replace(old, new)
    return content, counts


def scan_or_apply(root: Path, apply_text: bool) -> dict:
    table = build_replacement_table()
    report = {"files_changed": {}, "total_replacements": 0, "files_scanned": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d) + "/")]
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            if is_excluded(rel):
                continue
            if not is_text_candidate(fname):
                continue
            report["files_scanned"] += 1
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            new_content, counts = apply_text_replacements(content, table)
            if counts:
                report["files_changed"][rel] = counts
                report["total_replacements"] += sum(counts.values())
                if apply_text:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(new_content)
    return report


def rename_one(root: Path, old_path: Path, new_path: Path, in_git: bool) -> None:
    new_path.parent.mkdir(parents=True, exist_ok=True)
    if in_git:
        result = subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            cwd=root, capture_output=True, text=True,
        )
        if result.returncode != 0:
            old_path.rename(new_path)
    else:
        old_path.rename(new_path)


def apply_renames(root: Path) -> dict:
    renamed = {}
    in_git = (root / ".git").exists()

    items = sorted(MODULE_RENAMES.items(), key=lambda kv: -kv[0].count("/"))
    for old_rel, new_rel in items:
        old_path = root / old_rel
        new_path = root / new_rel
        if not old_path.exists():
            continue
        rename_one(root, old_path, new_path, in_git)
        renamed[old_rel] = new_rel

    table = build_replacement_table()
    all_paths = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d) + "/")]
        for name in filenames + dirnames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            if is_excluded(rel):
                continue
            all_paths.append(full)
    all_paths.sort(key=lambda p: -p.count(os.sep))

    for full in all_paths:
        if not os.path.exists(full):
            continue
        name = os.path.basename(full)
        new_name = name
        for old, new in table:
            if old in new_name:
                new_name = new_name.replace(old, new)
        if new_name != name:
            old_path = Path(full)
            new_path = old_path.parent / new_name
            rel_old = os.path.relpath(str(old_path), root)
            if rel_old in renamed:
                continue
            rename_one(root, old_path, new_path, in_git)
            renamed[rel_old] = os.path.relpath(str(new_path), root)

    return renamed


def syntax_check(root: Path) -> list:
    import ast
    errors = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d) + "/")]
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        ast.parse(f.read(), filename=fpath)
                except SyntaxError as e:
                    errors.append((os.path.relpath(fpath, root), str(e)))
    return errors


def import_sanity_check(root: Path) -> list:
    problems = []
    stale_names = [old for old, _ in MODULE_NAME_TEXT_REPLACEMENTS]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d) + "/")]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            if is_excluded(rel):
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            for stale in stale_names:
                if f"import {stale}" in content or f"from {stale} " in content or f"from {stale}." in content:
                    problems.append((rel, stale))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--apply-text", action="store_true")
    parser.add_argument("--apply-renames", action="store_true")
    parser.add_argument("--report", default="rebrand_report.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    print(f"Scanning {root} ...")
    text_report = scan_or_apply(root, apply_text=args.apply_text)

    if args.apply_renames:
        rename_report = apply_renames(root)
    else:
        rename_report = {old: new for old, new in MODULE_RENAMES.items() if (root / old).exists()}

    full_report = {
        "mode": {"apply_text": args.apply_text, "apply_renames": args.apply_renames},
        "text_replacements": text_report,
        "renames": rename_report,
    }
    with open(root / args.report, "w") as f:
        json.dump(full_report, f, indent=2)

    print(f"Files scanned:      {text_report['files_scanned']}")
    print(f"Files changed:      {len(text_report['files_changed'])}")
    print(f"Total replacements: {text_report['total_replacements']}")
    print(f"Renames {'applied' if args.apply_renames else 'planned'}: {len(rename_report)}")
    print(f"Report: {root / args.report}")

    if args.apply_text:
        print("\nPost-flight: syntax check...")
        errors = syntax_check(root)
        print("OK - no syntax errors." if not errors else f"!!! {len(errors)} syntax errors:")
        for p, e in errors[:20]:
            print(f"    {p}: {e}")

        print("\nPost-flight: stale module-name import check...")
        stale = import_sanity_check(root)
        print("OK - no stale imports." if not stale else f"!!! {len(stale)} stale imports:")
        for p, name in stale[:20]:
            print(f"    {p}: still references '{name}'")
    else:
        print("\n>>> DRY RUN - pass --apply-text to write changes. <<<")
    if not args.apply_renames:
        print(">>> Renames not applied - pass --apply-renames to execute. <<<")


if __name__ == "__main__":
    main()
