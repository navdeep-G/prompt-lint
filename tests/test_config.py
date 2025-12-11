from __future__ import annotations

from prompt_lint import lint_prompt
from prompt_lint.config import LintConfig, RuleOptions
from prompt_lint.models import Severity
from prompt_lint.rules import ALL_RULES


def test_config_can_disable_rule_and_override_severity():
    prompt = (
        "Write a very brief but extremely detailed report. "
        "Include as much detail as possible and write as much as you can."
    )

    # Sanity check: defaults should trigger both rules
    base_issues = lint_prompt(prompt, rules=ALL_RULES)
    base_rule_ids = {issue.rule_id for issue in base_issues}
    assert "conflicting-length" in base_rule_ids
    assert "unbounded-length" in base_rule_ids

    # Now configure:
    # - disable `conflicting-length`
    # - keep `unbounded-length` but bump severity to ERROR
    config = LintConfig(
        rules={
            "conflicting-length": RuleOptions(
                enabled=False,
            ),
            "unbounded-length": RuleOptions(
                enabled=True,
                severity=Severity.ERROR,
                # options could also customise `phrases` here if desired
            ),
        }
    )

    issues = lint_prompt(
        prompt,
        rules=ALL_RULES,
        config=config,
    )

    rule_ids = {issue.rule_id for issue in issues}
    assert "conflicting-length" not in rule_ids
    assert "unbounded-length" in rule_ids

    # Check the severity override is honored
    unbounded_severities = {
        issue.severity for issue in issues if issue.rule_id == "unbounded-length"
    }
    assert unbounded_severities == {Severity.ERROR}

