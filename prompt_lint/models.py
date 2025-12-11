from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LintIssue:
    """
    Represents a single lint issue found in a prompt.
    """

    rule_id: str
    message: str
    severity: Severity

    def as_dict(self) -> dict:
        return {
            "ruleId": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
        }
