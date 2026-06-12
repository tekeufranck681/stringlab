from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ENV: str = "development"

    # Exact frontend origin(s) allowed by CORS. A wildcard is not permitted when
    # credentials are included (the session cookie), so origins must be explicit.
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")


settings = Settings()
