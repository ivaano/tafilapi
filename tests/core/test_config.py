from app.core.config import Settings


def test_settings_defaults():
    """
    Test that Settings loads correct default configuration values.
    """
    settings = Settings()
    assert settings.API_AUTH_TOKEN == "default-super-secret-token"
    assert settings.PROJECT_NAME == "Tafilapi HTML Extractor"
    assert settings.LOG_LEVEL == "INFO"


def test_settings_custom_log_level(monkeypatch):
    """
    Test that Settings loads a custom LOG_LEVEL from environment variables.
    """
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = Settings()
    assert settings.LOG_LEVEL == "DEBUG"
