import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Customer Sentiment & Churn Risk Monitor"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev_secret_key_change_in_production_123456789"

    # Database
    DATABASE_URL: str = "sqlite:///./churn_monitor.db"  # Fallback to local SQLite if PostgreSQL is not specified
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # AI Configuration
    AI_PROVIDER: str = "ai_pipeline"  # "ai_pipeline", "openai", "gemini", "deterministic_rule"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    ENABLE_CLOUD_AI: bool = True
    CONFIDENCE_ESCALATION_THRESHOLD: float = 0.85
    AI_MAX_RETRIES: int = 3
    AI_TIMEOUT_SECONDS: float = 15.0

    # Automation / Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_INTERVAL_MINUTES: int = 5
    DATA_WATCH_DIR: str = "./data/incoming"
    AUTO_INGEST_SAMPLE_DATA: bool = True

    # Risk Engine Thresholds
    RISK_THRESHOLD_HIGH: int = 60
    RISK_THRESHOLD_CRITICAL: int = 80

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
