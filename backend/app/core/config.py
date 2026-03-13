from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db"
    email_host: str = ""
    email_user: str = ""
    email_app_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
