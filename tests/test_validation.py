import pytest

from sofoste_medical_center.validation import ValidationError, validate_record


def valid_form():
    return {"first_name": " Ada ", "last_name": "Lovelace", "birth_date": "1815-12-10"}


def test_validation_normalizes_and_fills_optional_fields():
    data = valid_form()
    data["birth_date"] = "1915-12-10"
    result = validate_record(data)
    assert result["first_name"] == "Ada"
    assert result["allergies"] == ""


def test_validation_rejects_missing_and_future_birth_date():
    with pytest.raises(ValidationError):
        validate_record({})
    data = valid_form()
    data["birth_date"] = "2999-01-01"
    with pytest.raises(ValidationError):
        validate_record(data)
