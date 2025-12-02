from __future__ import annotations

"""Compatibility module exposing the built‑in rule set.

Older versions of :mod:`prompt_lint` exposed ``ALL_RULES`` as a list of
simple functions. It is now a list of :class:`Rule` objects, but
:func:`prompt_lint.core.lint_prompt` still accepts the old function style,
so existing code like::

    from prompt_lint.core import lint_prompt
    from prompt_lint.rules import ALL_RULES

    issues = lint_prompt(prompt, rules=ALL_RULES)

continues to work.
"""

from .builtin_rules import BUILTIN_RULES

ALL_RULES = BUILTIN_RULES
