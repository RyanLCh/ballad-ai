from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "Ballad AI Backend"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["text/plain"]
    
    # Text processing settings
    CHUNK_SIZE: int = 500  # Characters per chunk
    CHUNK_OVERLAP: int = 50  # Overlap between chunks

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
