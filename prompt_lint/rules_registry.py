from __future__ import annotations

from importlib import metadata
from typing import Iterable, List

from .rule_types import Rule
from .builtin_rules import BUILTIN_RULES


def load_builtin_rules() -> List[Rule]:
    """Return the list of built‑in rules."""
    return list(BUILTIN_RULES)


def load_plugin_rules() -> List[Rule]:
    """Load rules exposed via the ``prompt_lint.rules`` entry‑point.

    Plugins should expose a callable that returns either a single
    :class:`Rule` or an iterable of :class:`Rule` objects.
    """
    rules: List[Rule] = []

    try:
        eps = metadata.entry_points()
    except Exception:  # pragma: no cover - extremely defensive
        return rules

    # Python 3.10+ has ``select``; older versions expose a mapping.
    group = None
    if hasattr(eps, "select"):
        group = eps.select(group="prompt_lint.rules")
    else:  # pragma: no cover
        group = eps.get("prompt_lint.rules", [])  # type: ignore[assignment]

    for ep in group:  # type: ignore[assignment]
        try:
            factory = ep.load()
            result = factory()
        except Exception:
            # A broken plugin should not crash the linter.
            continue

        if isinstance(result, Rule):
            rules.append(result)
        else:
            try:
                for rule in result:  # type: ignore[assignment]
                    if isinstance(rule, Rule):
                        rules.append(rule)
            except TypeError:
                continue

    return rules


def get_all_rules() -> List[Rule]:
    """Return built‑in rules plus any plugin rules."""
    return load_builtin_rules() + load_plugin_rules()
