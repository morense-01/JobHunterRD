from typing import Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from app.models.enums import RemoteType
from app.models.job import Job
from app.utils.hasher import HashGenerator
from .base import BaseScraper, ScraperResult


class GoogleJobsScraper(BaseScraper):
    SEARCH_URL = "/search?q=empleos+tecnologia+Santo+Domingo&ibp=htl;jobs"

    def scrape(self) -> ScraperResult:
        if not self._enabled:
            return ScraperResult(success=True, jobs=[], count=0)

        jobs: list[Job] = []
        url = f"{self._base_url}{self.SEARCH_URL}"

        try:
            response = requests.get(url, timeout=30, headers=self._headers())
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"GoogleJobsScraper: HTTP error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select("div[data-jsarouter], div.job-card, div.vacancy-card, li.vacancy")

            if not items:
                logger.warning("GoogleJobsScraper: No listings with primary selectors. Trying fallback.")
                items = soup.select("a[href*='employment'], a[href*='job'], div[role='listitem']")

            for item in items:
                job = self._parse_listing(item)
                if job:
                    jobs.append(job)

            logger.info(f"GoogleJobsScraper: Found {len(jobs)} jobs")
            return ScraperResult(success=True, jobs=jobs, count=len(jobs))

        except Exception as e:
            logger.error(f"GoogleJobsScraper: Parse error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

    def _headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-DO,es;q=0.9,en;q=0.8",
        }

    def _parse_listing(self, item: BeautifulSoup) -> Optional[Job]:
        try:
            title_el = item.select_one("h2, h3, .job-title, .title, [role='heading']")
            if not title_el:
                return None
            title = title_el.get_text(strip=True)

            link_el = item.select_one("a[href]")
            href = link_el.get("href") if link_el else ""
            url = href if href.startswith("http") else f"https://www.google.com{href}"

            company_el = item.select_one(".company, .employer, .empresa")
            company = company_el.get_text(strip=True) if company_el else "No especificada"

            location_el = item.select_one(".location, .ubicacion, .place")
            location = location_el.get_text(strip=True) if location_el else "No especificada"

            desc_el = item.select_one(".description, .descripcion, .summary")
            description = desc_el.get_text(strip=True) if desc_el else ""

            salary_el = item.select_one(".salary, .salario")
            salary = salary_el.get_text(strip=True) if salary_el else None

            job = Job(
                title=title,
                company=company,
                location=location,
                remote=RemoteType.UNKNOWN,
                salary=salary,
                description=description,
                url=url,
                portal="google_jobs",
            )
            job.hash = HashGenerator.generate(job.company, job.title, job.location)
            return job

        except Exception as e:
            logger.debug(f"GoogleJobsScraper: Error parsing item: {e}")
            return None
