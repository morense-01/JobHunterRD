from typing import Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from app.models.enums import RemoteType
from app.models.job import Job
from app.utils.hasher import HashGenerator
from .base import BaseScraper, ScraperResult


class LinkedInScraper(BaseScraper):
    SEARCH_URL = "/search?keywords=tecnologia&location=Santo%20Domingo&trk=public_jobs_jobs-search-bar_search-submit"

    def scrape(self) -> ScraperResult:
        if not self._enabled:
            return ScraperResult(success=True, jobs=[], count=0)

        jobs: list[Job] = []
        url = f"{self._base_url}{self.SEARCH_URL}"

        try:
            response = requests.get(url, timeout=30, headers=self._headers())
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"LinkedInScraper: HTTP error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select("li[data-occludable-job-id], div.base-card, div.job-search-card, article.job-card")

            if not items:
                logger.warning("LinkedInScraper: No listings with primary selectors. Trying fallback.")
                items = soup.select("a[href*='/jobs/view']")

            for item in items:
                job = self._parse_listing(item)
                if job:
                    jobs.append(job)

            logger.info(f"LinkedInScraper: Found {len(jobs)} jobs")
            return ScraperResult(success=True, jobs=jobs, count=len(jobs))

        except Exception as e:
            logger.error(f"LinkedInScraper: Parse error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

    def _headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-DO,es;q=0.9,en;q=0.8",
        }

    def _parse_listing(self, item: BeautifulSoup) -> Optional[Job]:
        try:
            title_el = item.select_one("h3 a, h3, .job-title, .base-search-card__title")
            if not title_el:
                return None
            title = title_el.get_text(strip=True)

            link_el = item.select_one("a[href*='/jobs/view'], a[href*='/jobs/search']")
            href = link_el.get("href") if link_el else ""
            url = href.split("?")[0] if href else ""

            company_el = item.select_one(".company, .base-search-card__subtitle, h4 a, h4")
            company = company_el.get_text(strip=True) if company_el else "No especificada"

            location_el = item.select_one(".location, .job-location, .base-search-card__metadata")
            location = location_el.get_text(strip=True) if location_el else "No especificada"

            desc_el = item.select_one(".description, .job-description")
            description = desc_el.get_text(strip=True) if desc_el else ""

            salary_el = item.select_one(".salary, .job-salary")
            salary = salary_el.get_text(strip=True) if salary_el else None

            remote_el = item.select_one(".remote, .workplace-type, .job-workplace-type")
            remote = self._parse_remote(remote_el.get_text(strip=True) if remote_el else "")

            job = Job(
                title=title,
                company=company,
                location=location,
                remote=remote,
                salary=salary,
                description=description,
                url=url,
                portal="linkedin",
            )
            job.hash = HashGenerator.generate(job.company, job.title, job.location)
            return job

        except Exception as e:
            logger.debug(f"LinkedInScraper: Error parsing item: {e}")
            return None

    @staticmethod
    def _parse_remote(text: str) -> RemoteType:
        text = text.lower()
        if "remoto" in text or "remote" in text:
            return RemoteType.REMOTE
        if "híbrido" in text or "hibrido" in text or "hybrid" in text:
            return RemoteType.HYBRID
        if "presencial" in text or "on-site" in text or "onsite" in text:
            return RemoteType.ON_SITE
        return RemoteType.UNKNOWN
