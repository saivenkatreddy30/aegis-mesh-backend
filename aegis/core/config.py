from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisMesh"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./aegis_mesh.db"

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()