from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    project: str = Field(..., min_length=1)
    owner: str = "Unknown"
    control_set: str = "Internal"
    version: str = "0.1.0"
    git_commit: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Finding(BaseModel):
    model_config = ConfigDict(extra="allow")

    finding_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    severity: Severity = Severity.MEDIUM
    status: str = "open"
    description: str | None = None
    source: str | None = None
    mapped_controls: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator("severity", mode="before")
    @classmethod
    def normalise_severity(cls, value: Any) -> Severity:
        if value is None:
            return Severity.MEDIUM

        if isinstance(value, Severity):
            return value

        text = str(value).strip().lower()
        aliases = {
            "informational": Severity.INFO,
            "moderate": Severity.MEDIUM,
            "med": Severity.MEDIUM,
            "critical/high": Severity.CRITICAL,
        }
        text = aliases.get(text, text)
        return Severity(text)


class EvidenceItem(BaseModel):
    path: str
    sha256: str
    size_bytes: int


class GenerationResult(BaseModel):
    findings_count: int
    evidence_count: int
    output_files: list[str]
