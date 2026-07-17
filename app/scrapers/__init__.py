from .base import BaseScraper, ScraperResult
from .aldaba import AldabaScraper
from .computrabajo import ComputrabajoScraper
from .linkedin import LinkedInScraper
from .google_jobs import GoogleJobsScraper

__all__ = [
    "BaseScraper",
    "ScraperResult",
    "AldabaScraper",
    "ComputrabajoScraper",
    "LinkedInScraper",
    "GoogleJobsScraper",
]
