from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys
    ASSEMBLYAI_API_KEY: str
    CARTESIA_API_KEY: str
    GROQ_API_KEY: str
    QDRANT_URL: str

    # App Settings
    APP_NAME: str = "Voice Interview Agent"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
