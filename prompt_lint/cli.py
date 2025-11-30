from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .core import lint_prompt


def _read_input(args: argparse.Namespace) -> str:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    # Read from stdin
    data = sys.stdin.read()
    if not data:
        raise SystemExit(
            "No prompt provided. Use --file or pipe a prompt into stdin.\n"
            "Example: echo 'Write a brief but detailed...' | prompt-lint"
        )
    return data


def _print_human_readable(issues) -> None:
    if not issues:
        print("✅ No issues found.")
        return

    for issue in issues:
        print(f"[{issue.severity.value.upper()}] {issue.rule_id}: {issue.message}")


def _print_json(issues) -> None:
    print(json.dumps([issue.as_dict() for issue in issues], indent=2))


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Static linter for LLM prompt strings."
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Path to a text file containing the prompt. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output issues as JSON instead of human-readable text.",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    prompt_text = _read_input(args)
    issues = lint_prompt(prompt_text)

    if args.json:
        _print_json(issues)
    else:
        _print_human_readable(issues)


if __name__ == "__main__":
    main()
