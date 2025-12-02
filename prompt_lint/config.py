from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .models import Severity

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore[assignment]
    except ModuleNotFoundError:  # pragma: no cover
        tomllib = None  # type: ignore[assignment]


@dataclass
class RuleOptions:
    """Per‑rule configuration loaded from ``prompt-lint.toml``."""

    enabled: bool = True
    severity: Optional[Severity] = None
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class LintConfig:
    """In‑memory representation of the config file."""

    rules: Mapping[str, RuleOptions] = field(default_factory=dict)

    def get_rule_options(self, rule_id: str) -> RuleOptions:
        return self.rules.get(rule_id, RuleOptions())


def _find_config_file(start: Optional[Path] = None) -> Optional[Path]:
    """Walk upwards from *start* looking for ``prompt-lint.toml``."""
    start = start or Path.cwd()
    for path in (start, *start.parents):
        candidate = path / "prompt-lint.toml"
        if candidate.is_file():
            return candidate
    return None


def _parse_severity(raw: str) -> Severity:
    value = raw.strip().lower()
    if value == "info":
        return Severity.INFO
    if value == "warning":
        return Severity.WARNING
    if value == "error":
        return Severity.ERROR
    raise ValueError(f"Unknown severity value in config: {raw!r}")


def load_config(path: str | Path | None = None) -> LintConfig:
    """Load a :class:`LintConfig` from ``prompt-lint.toml``.

    If *path* is ``None``, the file is discovered by walking up from the
    current working directory. If no file is found, an empty config is
    returned.
    """
    if path is None:
        cfg_path = _find_config_file()
        if cfg_path is None:
            return LintConfig()
    else:
        cfg_path = Path(path)
        if not cfg_path.is_file():
            raise FileNotFoundError(cfg_path)

    if tomllib is None:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "Reading prompt-lint config requires Python 3.11+ or the 'tomli' "
            "package to be installed."
        )

    with cfg_path.open("rb") as f:
        data = tomllib.load(f)

    rules_table = data.get("rules", {}) or {}
    rules: Dict[str, RuleOptions] = {}

    for rule_id, raw_opts in rules_table.items():
        if not isinstance(raw_opts, dict):
            continue

        enabled = bool(raw_opts.get("enabled", True))
        sev_raw = raw_opts.get("severity")
        severity = _parse_severity(sev_raw) if isinstance(sev_raw, str) else None

        options = {
            k: v
            for k, v in raw_opts.items()
            if k not in {"enabled", "severity"}
        }
        rules[rule_id] = RuleOptions(
            enabled=enabled,
            severity=severity,
            options=options,
        )

    return LintConfig(rules=rules)
