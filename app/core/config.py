from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Nostalgia API"
    database_url: str
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"


settings = Settings()
