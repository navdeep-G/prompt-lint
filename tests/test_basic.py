from __future__ import annotations

from prompt_lint import lint_prompt


def test_conflicting_length_and_unbounded():
    prompt = (
        "Write a very brief but extremely detailed report. "
        "Include as much detail as possible and write as much as you can."
    )

    issues = lint_prompt(prompt)
    rule_ids = {issue.rule_id for issue in issues}

    assert "conflicting-length" in rule_ids
    assert "unbounded-length" in rule_ids


def test_missing_format():
    prompt = "Explain how transformers work in machine learning."
    issues = lint_prompt(prompt)
    rule_ids = {issue.rule_id for issue in issues}

    assert "no-format-specified" in rule_ids


def test_clean_prompt_has_few_or_no_issues():
    prompt = (
        "You are an expert technical writer.\n"
        "Write a concise, bullet-point list of 5 key trade-offs of microservices vs monoliths in JSON."
    )
    issues = lint_prompt(prompt)
    # Should not trigger the length / unbounded / format rules
    rule_ids = {issue.rule_id for issue in issues}
    assert "conflicting-length" not in rule_ids
    assert "unbounded-length" not in rule_ids
    assert "no-format-specified" not in rule_ids
