from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Contract Intelligence Platform"
    ENV: str = "development"
    DEVELOPMENT_ORGANIZATION_ID: UUID = UUID(
        "00000000-0000-0000-0000-000000000001"
    )
    # the emulator key is public, it is the same on every machine
    COSMOS_ENDPOINT: str = "https://localhost:8081"
    COSMOS_KEY: str = (
        "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )
    COSMOS_DATABASE: str = "contract_platform"
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # local keeps files in UPLOAD_DIR, azure_blob needs the two below
    STORAGE_BACKEND: str = "local"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "contracts"


settings = Settings()
