from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from app.models.job import Job


@dataclass
class ScraperResult:
    success: bool = True
    jobs: list[Job] = field(default_factory=list)
    error: Optional[str] = None
    count: int = 0


class BaseScraper(ABC):
    def __init__(self, base_url: str, enabled: bool = True) -> None:
        self._base_url = base_url.rstrip("/")
        self._enabled = enabled

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Scraper", "").lower()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @abstractmethod
    def scrape(self) -> ScraperResult:
        ...
