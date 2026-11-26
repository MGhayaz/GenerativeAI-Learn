from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field,model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    google_api_key: str | None = None
    gemini_keys: list[str] = Field(default_factory=list)
    
    
    mongodb_connection_id : str = Field (
        ...,
        min_length=1
    )
    mongodb_connection_password : str = Field( 
        ...,
        min_length=1,
    )
# yahan bi env ke values dale kyuki agar .env se feilds missing hue toh yahan as default diye jaate [prority env to config]
    model_name: str = "gemini-3.5-flash-lite"
    model_temperature:int=0
    mongodb_database_name : str = "speaking_agent_conversation_logs"
    mongodb_regular_collection_name : str = "regular conversations"
    mongodb_turns_collection_name : str = "turns"

    tts_model: str = "gemini-3.1-flash-tts-preview"
    chat_closure_set : set = {
            "exit",
            "band hojao",
            "bye",
    }

    llm_max_retries: int = 3
    llm_retry_base_delay: float = 1.0
    llm_retry_max_delay: float = 8.0

    voice_name: str = "Leda"

    working_directory: Path
    max_tool_iterations = 5
    

    max_tool_iterations: int = Field(
        default=5,
        ge=1,
        le=20,
    )
    # to update this below value, run scripts.llm-smoke to get new constant config values like prommpt tokens, fixed_overhead_default and update them in core.config else prediction error 0.7% se ~3% ho jayega in mongo db docs on each turn
    fixed_overhead_default: int = 3963 # 3850 is old, changed on 26nov   # measured: system prompt + tool schemas (Phase 1) , Is value ko jab bhi system prompt ya tools badlo, dobara measure karna padega.
    command_timeout: int = Field(
        default=120,
        ge=1,
        le=600,
    )
    max_tool_output_chars: int = Field(
    default=4000,
    ge=200,
    le=50000,
    )
    # context window properties(Plan A, Phase 3b)
    input_budget_tokens: int = Field(default=16000, ge=2000)
    history_low_ratio: float = Field(default=0.6, ge=0.3, le=0.9)
    keep_full_turns: int = Field(default=2, ge=0)
    min_recent_turns: int = Field(default=2, ge=1)
    old_output_max_chars: int = Field(default=300, ge=50)
    chars_per_token: float = Field(default=3.5, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    @model_validator(mode="after")
    def validate_gemini_keys(self):
        keys = self.gemini_keys or (
            [self.google_api_key] if self.google_api_key else []
        )
        keys = [key.strip() for key in keys if key and key.strip()]

        if not keys:
            raise ValueError("Set GEMINI_KEYS or GOOGLE_API_KEY in .env")

        self.gemini_keys = keys
        return self


settings = Settings()