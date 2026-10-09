"""Configuration settings for QUANTA AI Engine."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI Engine settings loaded from environment."""

    APP_NAME: str = "QUANTA AI Decision Engine"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    AI_ENGINE_HOST: str = "0.0.0.0"
    AI_ENGINE_PORT: int = 8000
    
    # Financial Engine Defaults
    DEFAULT_STEP_SIZE: float = 5.0  # ₹ Cr increments
    DEFAULT_MIN_LIQUIDITY: float = 0.20
    DEFAULT_MAX_RISK: float = 0.30
    DEFAULT_RISK_TOLERANCE: float = 0.50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
