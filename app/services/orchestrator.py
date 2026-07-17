import time
from typing import Optional

from loguru import logger

from app.config.loader import Settings
from app.database.repository import DatabaseRepository
from app.filters.engine import FilterEngine
from app.models.job import Job
from app.notifications.telegram import TelegramNotifier
from app.scrapers.base import BaseScraper, ScraperResult


class Orchestrator:
    def __init__(
        self,
        settings: Settings,
        repository: DatabaseRepository,
        filter_engine: FilterEngine,
        notifier: TelegramNotifier,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._filter_engine = filter_engine
        self._notifier = notifier
        self._scrapers: list[BaseScraper] = []

    def register_scraper(self, scraper: BaseScraper) -> None:
        self._scrapers.append(scraper)

    def run_once(self) -> dict:
        start_time = time.time()
        logger.info("=" * 50)
        logger.info("JobHunterRD: Iniciando ciclo de búsqueda")
        logger.info("=" * 50)

        total_found = 0
        total_filtered = 0
        total_new = 0
        total_sent = 0
        portal_results: dict[str, dict] = {}

        for scraper in self._scrapers:
            portal_name = scraper.name
            logger.info(f"Consultando portal: {portal_name}")

            try:
                result: ScraperResult = scraper.scrape()
                portal_results[portal_name] = {
                    "success": result.success,
                    "found": result.count,
                    "error": result.error,
                }

                if not result.success:
                    logger.warning(f"{portal_name}: Error en scraping - {result.error}")
                    continue

                total_found += result.count
                logger.info(f"{portal_name}: {result.count} vacantes encontradas")

                for job in result.jobs:
                    filter_result = self._filter_engine.evaluate(job)
                    if not filter_result.passed:
                        logger.debug(f"Filtrado: {job.title} en {job.company} -> {filter_result.reason}")
                        total_filtered += 1
                        continue

                    saved = self._repository.save_job(job)
                    if saved is not None:
                        total_new += 1
                        logger.info(f"Nueva vacante: {job.title} - {job.company} ({portal_name})")

                        sent, error = self._notifier.send_vacancy(saved)
                        if sent:
                            self._repository.mark_as_notified(saved.id)
                            self._repository.register_notification(saved.id, "telegram", True)
                            total_sent += 1
                        else:
                            self._repository.register_notification(saved.id, "telegram", False, error)

            except Exception as e:
                logger.error(f"{portal_name}: Error inesperado: {e}")
                portal_results[portal_name] = {"success": False, "found": 0, "error": str(e)}

        elapsed = time.time() - start_time

        summary = {
            "portals": portal_results,
            "total_found": total_found,
            "total_filtered": total_filtered,
            "total_new": total_new,
            "total_sent": total_sent,
            "elapsed_seconds": round(elapsed, 2),
        }

        self._log_summary(summary)
        return summary

    def _log_summary(self, summary: dict) -> None:
        logger.info("-" * 50)
        logger.info("RESUMEN DEL CICLO")
        logger.info(f"  Portales consultados: {len(summary['portals'])}")
        logger.info(f"  Vacantes encontradas: {summary['total_found']}")
        logger.info(f"  Vacantes filtradas:   {summary['total_filtered']}")
        logger.info(f"  Vacantes nuevas:      {summary['total_new']}")
        logger.info(f"  Notificaciones enviadas: {summary['total_sent']}")
        logger.info(f"  Tiempo total:         {summary['elapsed_seconds']}s")

        for portal, result in summary["portals"].items():
            status = "OK" if result["success"] else "ERROR"
            logger.info(f"    [{status}] {portal}: {result['found']} vacantes")

        logger.info("=" * 50)
