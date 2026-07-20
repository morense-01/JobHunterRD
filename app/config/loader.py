import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from loguru import logger


class SchedulerConfig(BaseModel):
    interval_minutes: int = 20


class PortalConfig(BaseModel):
    enabled: bool = True
    base_url: str = ""


class PortalsConfig(BaseModel):
    aldaba: PortalConfig = PortalConfig()
    computrabajo: PortalConfig = PortalConfig()
    linkedin: PortalConfig = PortalConfig()
    google_jobs: PortalConfig = PortalConfig(enabled=False)


class TelegramConfig(BaseModel):
    bot_token: str = ""
    chat_id: str = ""


class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_addr: str = ""
    to_addr: str = ""


class Settings(BaseModel):
    scheduler: SchedulerConfig = SchedulerConfig()
    max_days_old: int = 30
    provinces: list[str] = Field(default_factory=list)
    portals: PortalsConfig = PortalsConfig()
    positive_keywords: list[str] = Field(default_factory=list)
    negative_keywords: list[str] = Field(default_factory=list)
    excluded_companies: list[str] = Field(default_factory=list)
    telegram: TelegramConfig = TelegramConfig()
    email: EmailConfig = EmailConfig()


class ConfigLoader:
    def __init__(self, config_path: str | Path) -> None:
        self._config_path = Path(config_path)
        self._settings: Optional[Settings] = None

    def load(self) -> Settings:
        raw: dict = {}

        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                raw = loaded
            logger.info(f"Configuration loaded from {self._config_path}")
        else:
            logger.warning(f"Config file not found: {self._config_path}. Using defaults.")

        self._apply_env_overrides(raw)
        self._settings = Settings(**raw)
        return self._settings

    @staticmethod
    def _apply_env_overrides(raw: dict) -> None:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if "telegram" not in raw:
            raw["telegram"] = {}
        if bot_token:
            raw["telegram"]["bot_token"] = bot_token
        if chat_id:
            raw["telegram"]["chat_id"] = chat_id

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            return self.load()
        return self._settings
