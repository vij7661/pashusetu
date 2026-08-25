from app.core.localization import SUPPORTED_LANGUAGES


def test_approved_languages_are_present():
    assert set(SUPPORTED_LANGUAGES) == {"te", "hi", "en", "mr", "ta", "ml"}
