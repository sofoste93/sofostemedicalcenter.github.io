from sofoste_medical_center.i18n import TEXT


def test_every_language_has_the_same_keys():
    expected = set(TEXT["fr"])
    assert all(set(messages) == expected for messages in TEXT.values())
