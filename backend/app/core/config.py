from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "PashuSetu API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://pashusetu:pashusetu@db:5432/pashusetu"
    jwt_secret: str = "change-me"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    otp_ttl_seconds: int = 300
    otp_max_attempts: int = 5
    otp_test_mode: bool = False
    database_isolated_for_qa: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    cors_origin_regex: str | None = None

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @model_validator(mode="after")
    def validate_otp_test_safety(self):
        database_name = make_url(self.database_url).database
        if self.otp_test_mode and (
            self.app_env.lower() not in {"local", "qa", "test"}
            or not self.database_isolated_for_qa
            or database_name not in {"pashusetu_qa", "pashusetu_test"}
        ):
            raise ValueError(
                "OTP test mode requires an isolated local/QA/test environment and named QA/test database"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
