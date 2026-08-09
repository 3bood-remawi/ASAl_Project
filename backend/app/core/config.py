from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Contract Intelligence Platform"
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5433/contract_platform"
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # local keeps files in UPLOAD_DIR, azure_blob needs the two below
    STORAGE_BACKEND: str = "local"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "contracts"


settings = Settings()