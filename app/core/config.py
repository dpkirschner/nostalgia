from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "Nostalgia API"
    database_url: str
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"
    log_format: str = "pretty"

    round_places: int = 6
    recent_months: int = 18
    outdated_tenancy_months: int = 18


settings = Settings()
