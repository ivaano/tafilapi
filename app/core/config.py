from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_AUTH_TOKEN: str = "default-super-secret-token"
    PROJECT_NAME: str = "Tafilapi HTML Extractor"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
