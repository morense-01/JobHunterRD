from typing import Optional

from bs4 import BeautifulSoup
from loguru import logger

from app.models.enums import RemoteType
from app.models.job import Job
from app.utils.hasher import HashGenerator
from .base import BaseScraper, ScraperResult


class ComputrabajoScraper(BaseScraper):
    SEARCH_URL = "/empleos?q=tecnologia"

    def scrape(self) -> ScraperResult:
        if not self._enabled:
            return ScraperResult(success=True, jobs=[], count=0)

        jobs: list[Job] = []
        url = f"{self._base_url}{self.SEARCH_URL}"

        try:
            html = self._render_page(url)
            if not html:
                return ScraperResult(success=False, jobs=[], error="Empty page after render")
        except Exception as e:
            logger.error(f"ComputrabajoScraper: Render error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

        try:
            soup = BeautifulSoup(html, "html.parser")

            items = soup.select(
                "article[class*='offer'], div[class*='offer'], div[class*='card'], "
                "li[data-offer-id], div[class*='result'], div[class*='list']"
            )

            if not items:
                items = soup.select("a[href*='/oferta/'], a[href*='/empleo/']")

            seen_titles = set()
            for item in items:
                job = self._parse_listing(item)
                if job and job.title not in seen_titles:
                    seen_titles.add(job.title)
                    jobs.append(job)

            logger.info(f"ComputrabajoScraper: Found {len(jobs)} jobs")
            return ScraperResult(success=True, jobs=jobs, count=len(jobs))

        except Exception as e:
            logger.error(f"ComputrabajoScraper: Parse error: {e}")
            return ScraperResult(success=False, jobs=[], error=str(e))

    def _render_page(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed, falling back to requests")
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "es-DO,es;q=0.9,en;q=0.8",
            }
            r = requests.get(url, timeout=30, headers=headers)
            r.raise_for_status()
            return r.text

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Playwright render failed: {e}")
            return None

    def _parse_listing(self, item: BeautifulSoup) -> Optional[Job]:
        try:
            title_el = (
                item.select_one("h2 a, h3 a, [class*='title'] a, [class*='titulo'] a")
                or item.select_one("h2, h3, [class*='title'], [class*='titulo']")
            )
            if not title_el:
                return None

            title = title_el.get_text(strip=True)

            link_el = item.select_one("a[href]")
            href = link_el.get("href") if link_el else ""
            url = href if href.startswith("http") else f"{self._base_url}{href}"

            company_el = item.select_one("[class*='company'], [class*='empresa'], [class*='name']")
            company = company_el.get_text(strip=True) if company_el else "No especificada"

            location_el = item.select_one("[class*='location'], [class*='ubicacion'], [class*='city']")
            location = location_el.get_text(strip=True) if location_el else "No especificada"

            desc_el = item.select_one("[class*='description'], [class*='descripcion'], [class*='resumen']")
            description = desc_el.get_text(strip=True) if desc_el else ""

            salary_el = item.select_one("[class*='salary'], [class*='salario']")
            salary = salary_el.get_text(strip=True) if salary_el else None

            job = Job(
                title=title,
                company=company,
                location=location,
                remote=RemoteType.UNKNOWN,
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
