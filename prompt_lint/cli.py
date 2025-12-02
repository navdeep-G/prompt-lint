from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .config import LintConfig, load_config
from .core import lint_prompt


def _read_prompt_from_file(path: str) -> str:
    return Path(path).read_text(encoding="utf8")


def _read_prompt_from_stdin() -> str:
    return sys.stdin.read()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Static linter for LLM prompt strings.",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a prompt text file. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human‑readable output.",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to prompt-lint.toml (overrides automatic discovery).",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Disable automatic config discovery.",
    )

    args = parser.parse_args(argv)

    if args.file:
        prompt = _read_prompt_from_file(args.file)
    else:
        if sys.stdin.isatty():
            parser.error("No --file provided and no data on stdin.")
        prompt = _read_prompt_from_stdin()

    if args.no_config:
        cfg = LintConfig()
        load_from_disk = False
    elif args.config:
        cfg = load_config(args.config)
        load_from_disk = False
    else:
        cfg = None
        load_from_disk = True

    issues = lint_prompt(
        prompt,
        config=cfg,
        load_config_from_disk=load_from_disk,
    )

    if args.json:
        payload = [issue.as_dict() for issue in issues]
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for issue in issues:
            print(f"[{issue.severity.value.upper()}] {issue.rule_id}: {issue.message}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
