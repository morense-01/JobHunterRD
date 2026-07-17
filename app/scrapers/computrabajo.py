from typing import Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from app.models.enums import RemoteType
from app.models.job import Job
from app.utils.hasher import HashGenerator
from .base import BaseScraper, ScraperResult


class ComputrabajoScraper(BaseScraper):
    SEARCH_URL = "/empleos?q=tecnologia&provincia="

    def scrape(self) -> ScraperResult:
        if not self._enabled:
            return ScraperResult(success=True, jobs=[], count=0)

        jobs: list[Job] = []
        url = f"{self._base_url}{self.SEARCH_URL}"

        try:
            response = requests.get(url, timeout=30, headers=self._headers())
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"ComputrabajoScraper: HTTP error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select("div.js-offer, article.b-row, div.box_offer, li[data-offer-id]")

            if not items:
                logger.warning("ComputrabajoScraper: No listings found with primary selectors. Trying fallback.")
                items = soup.select("a[href*='ofertas'], a[href*='empleo'], a[href*='job']")

            for item in items:
                job = self._parse_listing(item)
                if job:
                    jobs.append(job)

            logger.info(f"ComputrabajoScraper: Found {len(jobs)} jobs")
            return ScraperResult(success=True, jobs=jobs, count=len(jobs))

        except Exception as e:
            logger.error(f"ComputrabajoScraper: Parse error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

    def _headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-DO,es;q=0.9,en;q=0.8",
        }

    def _parse_listing(self, item: BeautifulSoup) -> Optional[Job]:
        try:
            title_el = item.select_one("h2 a, h3 a, .job-title a, .titulo-oferta a, a[title]")
            if not title_el:
                title_el = item.select_one("h2, h3, .job-title, .titulo-oferta")
            if not title_el:
                return None

            title = title_el.get_text(strip=True)
            link_el = title_el if title_el.name == "a" and title_el.get("href") else item.select_one("a[href]")
            href = link_el.get("href") if link_el else ""
            url = href if href.startswith("http") else f"{self._base_url}{href}"

            company_el = item.select_one(".company, .empresa, .name_company, .nombre-empresa")
            company = company_el.get_text(strip=True) if company_el else "No especificada"

            location_el = item.select_one(".location, .ubicacion, .city, .ciudad")
            location = location_el.get_text(strip=True) if location_el else "No especificada"

            desc_el = item.select_one(".description, .descripcion, .resumen")
            description = desc_el.get_text(strip=True) if desc_el else ""

            salary_el = item.select_one(".salary, .salario, .price")
            salary = salary_el.get_text(strip=True) if salary_el else None

            remote_el = item.select_one(".modalidad, .remote, .trabajo-remoto")
            remote = self._parse_remote(remote_el.get_text(strip=True) if remote_el else "")

            job = Job(
                title=title,
                company=company,
                location=location,
                remote=remote,
                salary=salary,
                description=description,
                url=url,
                portal="computrabajo",
            )
            job.hash = HashGenerator.generate(job.company, job.title, job.location)
            return job

        except Exception as e:
            logger.debug(f"ComputrabajoScraper: Error parsing item: {e}")
            return None

    @staticmethod
    def _parse_remote(text: str) -> RemoteType:
        text = text.lower()
        if "remoto" in text or "remote" in text:
            return RemoteType.REMOTE
        if "híbrido" in text or "hibrido" in text or "hybrid" in text:
            return RemoteType.HYBRID
        if "presencial" in text or "oficina" in text:
            return RemoteType.ON_SITE
        return RemoteType.UNKNOWN
