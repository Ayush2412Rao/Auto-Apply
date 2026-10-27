import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

class Settings(BaseSettings):
    APP_NAME: str = "Auto-Apply Agentic AI Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "auto-apply-super-secret-key-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/career_navigator.db"
    SYNC_DATABASE_URL: str = "sqlite:///./data/career_navigator.db"

    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chromadb")
    RESUME_STORAGE_DIR: str = str(BASE_DIR / "data" / "resumes")
    TAILORED_RESUME_DIR: str = str(BASE_DIR / "data" / "resumes" / "tailored")
    SCREENSHOT_DIR: str = str(BASE_DIR / "data" / "screenshots")

    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # Scrapy Standalone Crawler Settings
    SCRAPY_DOWNLOAD_DELAY: float = 0.5
    SCRAPY_CONCURRENT_REQUESTS: int = 4
    SCRAPY_DEFAULT_SPIDERS: str = "instahyre,hirist,remote_jobs,tech_jobs"

    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    IMAP_HOST: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    ALERT_SENDER_EMAIL: str = ""
    ALERT_RECIPIENT_EMAIL: str = ""

    TIMEZONE: str = "Asia/Kolkata"
    SCHEDULER_INTERVAL_HOURS: int = 1
    MAX_APPLICATIONS_PER_HOUR: int = 5
    MAX_APPLICATIONS_PER_DAY: int = 25
    MIN_MATCH_SCORE_DEFAULT: int = 75

    DEFAULT_AUTOMATION_POLICY: str = "automatic"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_gemini_key(self) -> str:
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY", "")

settings = Settings()

for folder in [
    settings.CHROMA_PERSIST_DIR,
    settings.RESUME_STORAGE_DIR,
    settings.TAILORED_RESUME_DIR,
    settings.SCREENSHOT_DIR,
    str(BASE_DIR / "data")
]:
    Path(folder).mkdir(parents=True, exist_ok=True)
