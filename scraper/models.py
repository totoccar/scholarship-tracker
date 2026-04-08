from datetime import date, timedelta
from typing import Literal

from dateutil import parser as date_parser
from pydantic import BaseModel, Field, HttpUrl, field_validator


def _parse_deadline_text(raw_deadline: str) -> str:
    if not raw_deadline:
        return (date.today() + timedelta(days=365)).isoformat()

    cleaned = raw_deadline.strip()
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = cleaned.replace("de estar", "")
    cleaned = cleaned.replace("estar", "")

    try:
        parsed = date_parser.parse(cleaned, fuzzy=True, dayfirst=True).date()
        return parsed.isoformat()
    except (ValueError, OverflowError):
        return (date.today() + timedelta(days=365)).isoformat()


class ScholarshipPayload(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=5000)
    provider: str = Field(min_length=2, max_length=150)
    country: str = Field(default="Global", max_length=100)
    deadline: str
    url: HttpUrl
    status: Literal["PENDING", "APPROVED", "REVIEW", "REJECTED"] = "PENDING"
    benefits: str = Field(default="", max_length=500)
    logoUrl: HttpUrl | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("deadline")
    @classmethod
    def validate_deadline_iso(cls, value: str) -> str:
        return _parse_deadline_text(value)

    @field_validator("tags")
    @classmethod
    def sanitize_tags(cls, tags: list[str]) -> list[str]:
        cleaned = []
        for tag in tags:
            normalized = tag.strip()
            if normalized and len(normalized) <= 50:
                cleaned.append(normalized)
        return cleaned[:15]


def normalize_deadline(raw_deadline: str) -> str:
    return _parse_deadline_text(raw_deadline)