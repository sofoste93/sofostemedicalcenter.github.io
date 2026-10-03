"""Input validation kept separate so it can be taught and tested easily."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

FIELDS = {
    "first_name": 60,
    "last_name": 60,
    "birth_date": 10,
    "sex": 30,
    "blood_type": 8,
    "emergency_contact": 100,
    "allergies": 500,
    "conditions": 500,
    "medications": 500,
    "notes": 500,
}
REQUIRED = {"first_name", "last_name", "birth_date"}


class ValidationError(ValueError):
    pass


def validate_record(form: Mapping[str, str]) -> dict[str, str]:
    record: dict[str, str] = {}
    for field, maximum in FIELDS.items():
        value = " ".join(form.get(field, "").strip().split())
        if field in REQUIRED and not value:
            raise ValidationError(f"{field} is required")
        if len(value) > maximum:
            raise ValidationError(f"{field} is too long")
        record[field] = value

    try:
        born = date.fromisoformat(record["birth_date"])
    except ValueError as exc:
        raise ValidationError("birth_date is invalid") from exc
    if born > date.today() or born.year < 1900:
        raise ValidationError("birth_date is invalid")
    return record
