from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    google_api_key: str = Field(
        ...,
        min_length=1,
    )
# yahan bi env ke values dale kyuki agar .env se feilds missing hue toh yahan as default diye jaate [prority env to config]
    model_name: str = "gemini-3.6-flash"

    tts_model: str = "gemini-3.1-flash-tts-preview"

    voice_name: str = "Leda"

    working_directory: Path

    max_tool_iterations: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    command_timeout: int = Field(
        default=120,
        ge=1,
        le=600,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()