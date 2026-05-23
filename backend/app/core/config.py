from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://crm_user:crm_password@localhost:5432/crm_db"
    email_host: str = ""
    email_user: str = ""
    email_app_password: str = ""

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg://", 1)
            elif v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg://", 1)
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
