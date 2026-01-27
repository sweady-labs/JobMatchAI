#!/usr/bin/env python3
"""Normalize .md filename endings recursively from current working dir or specified roots.

Usage:
  normalize_mds.py [--roots ROOTS [ROOTS ...]] [--dry-run] [--verbose]

If no --roots are provided the script will operate on the current working
directory (so you can run it from anywhere and it will normalize files under
that path).
"""

import argparse
import os
from pathlib import Path


def normalize_name(filename: str) -> str:
    lower = filename.lower()
    pos = lower.rfind(".md")
    if pos == -1:
        return filename
    base = filename[:pos]
    base_clean = base.rstrip(" .\t\n\r\x0b\x0c\u200b\ufeff")
    return base_clean + ".md"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    parent = path.parent
    suffix = path.suffix
    i = 1
    while True:
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def collect_and_normalize(roots, dry_run=False, verbose=False):
    changes = []
    for root in roots:
        root_p = Path(root).expanduser().resolve()
        if not root_p.exists():
            if verbose:
                print(f"Skip non-existent root: {root_p}")
            continue
        for dirpath, _, filenames in os.walk(root_p):
            for filename in filenames:
                new_filename = normalize_name(filename)
                if new_filename == filename:
                    continue
                old_path = Path(dirpath) / filename
                new_path = Path(dirpath) / new_filename
                if new_path.exists():
                    new_path = unique_path(new_path)
                    if verbose:
                        print(f"Collision, will use: {new_path}")
                changes.append((old_path, new_path))

    for old_path, new_path in changes:
        if verbose or dry_run:
            print(f"Rename: {old_path} -> {new_path}")
        if not dry_run:
            try:
                old_path.rename(new_path)
            except Exception as e:
                print(f"Error renaming {old_path} -> {new_path}: {e}")

    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Normalize .md filenames recursively")
    parser.add_argument(
        "--roots",
        nargs="+",
        help="Root paths to process (default: current working dir)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show planned renames without applying"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args(argv)

    if args.roots:
        roots = args.roots
    else:
        roots = [str(Path.cwd())]

    if args.verbose:
        print("Roots to process:")
        for r in roots:
            print(" -", r)

    changes = collect_and_normalize(roots, dry_run=args.dry_run, verbose=args.verbose)
    if args.dry_run:
        print(f"Dry run: {len(changes)} candidate(s) found")
    else:
        print(f"Completed: {len(changes)} file(s) renamed")


if __name__ == "__main__":
    main()
