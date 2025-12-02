from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class Severity(str, Enum):
    """Severity level for lint issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LintIssue:
    """Represents a single lint issue emitted by a rule."""

    rule_id: str
    message: str
    severity: Severity = Severity.WARNING
    data: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON‑serialisable representation of this issue."""
        result: Dict[str, Any] = {
            "ruleId": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
        }
        if self.data:
            result["data"] = self.data
        return result
