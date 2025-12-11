# prompt-lint

Static linter for LLM prompt strings.  
Think ESLint, but for prompts.

`prompt-lint` analyzes your prompt text and emits **lint issues** such as:

- Conflicting instructions: “be brief” and “extremely detailed”
- Unbounded output requests: “write as much as you can”
- Missing explicit output format
- Multiple tasks squeezed into one prompt
- Vague objectives like “etc.” or “and so on”

It’s rule-based, fast, and easy to extend.

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/your-username/prompt-lint.git
cd prompt-lint
pip install -e .
```

> Requires Python 3.9+

---

## Usage

### As a Python library

```python
from prompt_lint import lint_prompt

prompt = """
You are an expert technical writer and software architect.

Write a very brief but extremely detailed report about the system design
for a large-scale chat application.
Include as much detail as possible and write as much as you can.

Explain everything clearly.
"""

issues = lint_prompt(prompt)

for issue in issues:
    print(f"[{issue.severity.value.upper()}] {issue.rule_id}: {issue.message}")
```

Example output:

```text
[WARNING] conflicting-length: Prompt contains conflicting length instructions (e.g. both 'brief' and 'detailed').
[WARNING] unbounded-length: Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').
[INFO] no-format-specified: Prompt does not specify an explicit output format (e.g. JSON, list, table, bullet points).
```

You can also get the issues as plain dictionaries:

```python
dict_issues = [issue.as_dict() for issue in issues]
```

---

### As a CLI

The package includes a small `prompt-lint` CLI.

#### From stdin

```bash
echo "Write a brief but extremely detailed report. Write as much as you can." | prompt-lint
```

Example output:

```text
[WARNING] conflicting-length: Prompt contains conflicting length instructions (e.g. both 'brief' and 'detailed').
[WARNING] unbounded-length: Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').
[INFO] no-format-specified: Prompt does not specify an explicit output format (e.g. JSON, list, table, bullet points).
```

#### From a file

```bash
prompt-lint --file path/to/prompt.txt
```

#### JSON output

```bash
echo "Write as much as you can." | prompt-lint --json
```

Example:

```json
[
  {
    "ruleId": "unbounded-length",
    "message": "Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').",
    "severity": "warning"
  }
]
```

---

## Rules included (v0.1.0)

Current built-in rules:

- **`conflicting-length`** (warning)  
  Detects conflicting instructions like “brief” + “detailed”.

- **`unbounded-length`** (warning)  
  Flags phrases that suggest unbounded output, like “as much as you can”.

- **`no-format-specified`** (info)  
  If the prompt seems to ask for work but doesn’t specify a format (JSON, list, table, bullets, etc).

- **`vague-objective`** (info)  
  Warns on vague endings like “etc.” or “and so on”.

- **`multiple-tasks`** (info)  
  Heuristic for “too many tasks in one prompt” (multiple verbs + “also”).

- **`missing-role`** (info)  
  Suggests defining a clear role/persona for the model when instructions seem to be given.

---

## Extending with your own rules

Rules are simple functions:

```python
from typing import List
from prompt_lint.models import LintIssue, Severity

def my_custom_rule(prompt: str) -> List[LintIssue]:
    if "TODO" in prompt:
        return [
            LintIssue(
                rule_id="contains-todo",
                severity=Severity.WARNING,
                message="Prompt contains 'TODO', which may indicate incomplete instructions.",
            )
        ]
    return []
```

You can call `lint_prompt` with a custom rule set:

```python
from prompt_lint.core import lint_prompt
from prompt_lint.rules import ALL_RULES
from my_project.rules import my_custom_rule

issues = lint_prompt(prompt_text, rules=ALL_RULES + [my_custom_rule])
```

---

## Development

Run tests:

```bash
pip install -e .
pip install pytest
pytest
```

---

## Status

This is an early, experimental tool intended as a lightweight helper for people building LLM-backed applications.

Contributions, rule ideas, and issues are welcome. 🙌
