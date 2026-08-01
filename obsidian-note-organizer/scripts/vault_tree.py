#!/usr/bin/env python3
"""vault_tree.py — print an Obsidian vault as an indented tree.

Pure Python stdlib. Prunes bookkeeping dirs so the output reflects only
note content.

Usage:
    vault_tree.py <vault-root> [--max-depth N] [--include-hidden]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PRUNE_DIRS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__"}
PRUNE_FILES = {".DS_Store", "thumbs.db"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("vault", help="path to Obsidian vault root")
    ap.add_argument("--max-depth", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--include-hidden", action="store_true", help="show dotfiles")
    args = ap.parse_args()

    root = Path(args.vault).expanduser()
    if not root.exists():
        print(f"ERROR: vault not found: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    print(f"{root}/")
    _walk(root, prefix="", depth=1, max_depth=args.max_depth, include_hidden=args.include_hidden)
    return 0


def _walk(dir_path: Path, prefix: str, depth: int, max_depth: int, include_hidden: bool) -> None:
    if max_depth and depth > max_depth:
        return
    try:
        entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return

    visible = [
        e for e in entries
        if (include_hidden or not e.name.startswith("."))
        and e.name not in PRUNE_DIRS
        and e.name not in PRUNE_FILES
    ]
    for i, entry in enumerate(visible):
        last = i == len(visible) - 1
        branch = "└── " if last else "├── "
        if entry.is_dir():
            print(f"{prefix}{branch}{entry.name}/")
            extension = "    " if last else "│   "
            _walk(entry, prefix + extension, depth + 1, max_depth, include_hidden)
        else:
            print(f"{prefix}{branch}{entry.name}")


if __name__ == "__main__":
    raise SystemExit(main())
