prompt-lint: Static Linter for LLM Prompt Strings
=================================================

> Think ESLint, but for prompts.

**prompt-lint** analyzes your prompt text and emits lint issues such as:

-   Conflicting instructions: "be brief" and "extremely detailed"

-   Unbounded output requests: "write as much as you can"

-   Missing explicit output format

-   Multiple tasks squeezed into one prompt

-   Vague objectives like "etc." or "and so on"

-   Missing model role/persona when giving instructions

It's **rule-based**, **fast**, and easy to extend and configure.

* * * * *

Installation
------------

Clone the repo and install in editable mode:

Bash

```
git clone https://github.com/your-username/prompt-lint.git
cd prompt-lint
pip install -e .

```

Requires **Python 3.9+**

* * * * *

Usage
-----

### As a Python Library

Python

```
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

**Example output:**

```
[WARNING] conflicting-length: Prompt contains conflicting length instructions (e.g. both 'brief' and 'detailed').
[WARNING] unbounded-length: Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').
[INFO] no-format-specified: Prompt does not specify an explicit output format (e.g. JSON, list, table, bullet points).

```

You can also get the issues as plain dictionaries:

Python

```
dict_issues = [issue.as_dict() for issue in issues]

```

#### Using a Config Object Directly

If you want to control rules programmatically:

Python

```
from prompt_lint import lint_prompt
from prompt_lint.config import load_config

config = load_config("prompt-lint.toml")
issues = lint_prompt(prompt, config=config)

```

If you don't pass a config, **prompt-lint** will automatically look for a `prompt-lint.toml` file by walking up from the current working directory.

### As a CLI

The package includes a small `prompt-lint` CLI.

#### From stdin

Bash

```
echo "Write a brief but extremely detailed report. Write as much as you can." | prompt-lint

```

**Example output:**

```
[WARNING] conflicting-length: Prompt contains conflicting length instructions (e.g. both 'brief' and 'detailed').
[WARNING] unbounded-length: Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').
[INFO] no-format-specified: Prompt does not specify an explicit output format (e.g. JSON, list, table, bullet points).

```

#### From a file

Bash

```
prompt-lint --file path/to/prompt.txt

```

#### JSON output

Bash

```
echo "Write as much as you can." | prompt-lint --json

```

**Example:**

JSON

```
[
  {
    "ruleId": "unbounded-length",
    "message": "Prompt encourages unbounded output length (e.g. 'as much as you can', 'as much detail as possible').",
    "severity": "warning"
  }
]

```

#### Config-related CLI options

| **Option** | **Description** |
| --- | --- |
| `--config PATH` | Use a specific `prompt-lint.toml` file. |
| `--no-config` | Disable automatic config discovery. |
| (default) | If neither is passed, `prompt-lint` will look for `prompt-lint.toml` starting from the current directory and walking upwards. |

* * * * *

Configuration (`prompt-lint.toml`)
----------------------------------

You can configure rules per-project with a `prompt-lint.toml` at the root of your repo.

Each rule has a table under `[rules.<rule-id>]`:

-   `enabled` -- `true` / `false` (default: `true`)

-   `severity` -- `"info"`, `"warning"`, or `"error"`

-   Any additional keys are passed as options to that rule

**Example:**

Ini, TOML

```
[rules.conflicting-length]
enabled = true
severity = "warning"
group_a = ["brief", "short", "succinct"]
group_b = ["detailed", "thorough", "exhaustive"]

[rules.unbounded-length]
enabled = true
severity = "warning"
phrases = [
  "as much as you can",
  "write as much as possible",
  "as much detail as possible",
]

[rules.no-format-specified]
enabled = true
severity = "info"

[rules.multiple-tasks]
enabled = true
severity = "info"
max_tasks = 2

[rules.missing-role]
enabled = true
severity = "info"

```

If a rule is not mentioned in the config, it uses its built-in defaults.

* * * * *

Built-in Rules
--------------

Current built-in rules (exposed via `prompt_lint.rules.ALL_RULES`):

-   **conflicting-length** (`warning`)

    -   Detects conflicting instructions like "brief" + "detailed".

    -   **Config options:**

        -   `group_a` -- list of "short" keywords (default: `["brief", "short", "concise", "succinct"]`)

        -   `group_b` -- list of "long/detailed" keywords

        -   `message` -- custom message

-   **unbounded-length** (`warning`)

    -   Flags phrases that suggest unbounded output, like "as much as you can".

    -   **Config options:**

        -   `phrases` -- list of phrases that indicate unboundedness

        -   `message` -- custom message

-   **no-format-specified** (`info`)

    -   If the prompt seems to ask for work but doesn't specify a format (JSON, list, table, bullets, etc).

    -   **Config options:**

        -   `needles` -- phrases that count as specifying a format

        -   `message` -- custom message

-   **vague-objective** (`info`)

    -   Warns on vague endings like "etc." or "and so on".

    -   **Config options:**

        -   `phrases` -- vague/hand-wavy phrases you want to discourage

        -   `message` -- custom message

-   **multiple-tasks** (`info`)

    -   Heuristic for "too many tasks in one prompt" (multiple verbs + "also").

    -   **Config options:**

        -   `max_tasks` -- maximum allowed tasks before warning

        -   `message` -- custom message

-   **missing-role** (`info`)

    -   Suggests defining a clear role/persona for the model when instructions seem to be given.

    -   **Config options:**

        -   `message` -- custom message

* * * * *

Rule Model
----------

Internally, rules are first-class objects:

Python

```
from dataclasses import dataclass
from typing import Callable, List, Mapping, Any
from prompt_lint.models import LintIssue, Severity

CheckerFn = Callable[[str, Mapping[str, Any]], List[LintIssue]]

@dataclass
class Rule:
    id: str
    description: str
    default_severity: Severity
    checker: CheckerFn
    default_options: Mapping[str, Any]
    tags: set[str]

```

The checker receives:

1.  `prompt`: `str`

2.  `options`: `Mapping[str, Any]` -- merged from the rule's `default_options` and the per-rule section in `prompt-lint.toml`.

You normally don't need to construct `Rule` objects manually unless you are building a plugin or doing advanced integration.

* * * * *

Extending with Your Own Rules
-----------------------------

You can extend **prompt-lint** in two ways:

### 1\. Legacy Function-Style Rules (simple)

The simplest option: write a function that takes a prompt and returns a list of `LintIssue`.

Python

```
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

Python

```
from prompt_lint.core import lint_prompt
from prompt_lint.rules import ALL_RULES
from my_project.rules import my_custom_rule

issues = lint_prompt(prompt_text, rules=ALL_RULES + [my_custom_rule])

```

Function-style rules are automatically wrapped into `Rule` objects, so they keep working with config and the newer internals.

### 2\. Rule Objects + Plugins (advanced)

For more control (options, metadata, tagging, plugins), you can define full `Rule` objects and expose them via entry points.

Python

```
# my_project/prompt_rules.py
from typing import List, Mapping, Any
from prompt_lint.models import LintIssue, Severity
from prompt_lint.rule_types import Rule

def my_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    banned = options.get("banned", ["TODO"])
    hits = [b for b in banned if b in prompt]
    if not hits:
        return []

    return [
        LintIssue(
            rule_id="contains-banned-token",
            severity=Severity.ERROR,
            message=f"Prompt contains banned tokens: {', '.join(hits)}",
        )
    ]

MY_RULE = Rule(
    id="contains-banned-token",
    description="Flags banned tokens in prompts.",
    default_severity=Severity.ERROR,
    checker=my_checker,
    default_options={"banned": ["TODO"]},
    tags={"style"},
)

def get_rules():
    # Can return a single Rule or an iterable of Rules
    return [MY_RULE]

```

Then expose it in your `pyproject.toml`:

Ini, TOML

```
[project.entry-points."prompt_lint.rules"]
my_project_rules = "my_project.prompt_rules:get_rules"

```

Installed packages that declare this entry point will have their rules loaded automatically alongside the built-in rules.

* * * * *

Development
-----------

Run tests:

Bash

```
pip install -e .
pip install pytest
pytest

```

* * * * *

Status
------

This is an early, experimental tool intended as a lightweight helper for people building LLM-backed applications.

Contributions, rule ideas, and issues are welcome.
