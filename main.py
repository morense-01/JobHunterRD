import argparse
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.config.loader import ConfigLoader
from app.database.repository import DatabaseRepository
from app.filters.engine import FilterEngine
from app.notifications.telegram import TelegramNotifier
from app.scheduler.manager import SchedulerManager
from app.scrapers import AldabaScraper, ComputrabajoScraper, LinkedInScraper, GoogleJobsScraper
from app.services.orchestrator import Orchestrator
from app.utils.logger import setup_logger

load_dotenv()

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.yaml"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "jobhunter.db"


def bootstrap() -> tuple:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    setup_logger(LOGS_DIR)

    config_loader = ConfigLoader(CONFIG_PATH)
    settings = config_loader.load()

    repository = DatabaseRepository(DB_PATH)

    filter_engine = FilterEngine(
        provinces=settings.provinces,
        positive_keywords=settings.positive_keywords,
        negative_keywords=settings.negative_keywords,
        excluded_companies=settings.excluded_companies,
        max_days_old=settings.max_days_old,
    )

    notifier = TelegramNotifier(
        bot_token=settings.telegram.bot_token,
        chat_id=settings.telegram.chat_id,
    )

    orchestrator = Orchestrator(
        settings=settings,
        repository=repository,
        filter_engine=filter_engine,
        notifier=notifier,
    )

    scrapers = [
        AldabaScraper(
            base_url=settings.portals.aldaba.base_url,
            enabled=settings.portals.aldaba.enabled,
        ),
        ComputrabajoScraper(
            base_url=settings.portals.computrabajo.base_url,
            enabled=settings.portals.computrabajo.enabled,
        ),
        LinkedInScraper(
            base_url=settings.portals.linkedin.base_url,
            enabled=settings.portals.linkedin.enabled,
        ),
        GoogleJobsScraper(
            base_url=settings.portals.google_jobs.base_url,
            enabled=settings.portals.google_jobs.enabled,
        ),
    ]

    for scraper in scrapers:
        orchestrator.register_scraper(scraper)

    return settings, orchestrator


def run_once() -> None:
    _, orchestrator = bootstrap()
    orchestrator.run_once()


def run_scheduler() -> None:
    settings, orchestrator = bootstrap()

    def run_job() -> None:
        orchestrator.run_once()

    scheduler = SchedulerManager(
        interval_minutes=settings.scheduler.interval_minutes,
        job_func=run_job,
    )

    def handle_shutdown(signum, frame) -> None:
        from loguru import logger as log
        log.info("Shutdown signal received. Stopping scheduler...")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    run_job()
    scheduler.start()

    from loguru import logger as log
    log.info(f"JobHunterRD running. Next cycle in {settings.scheduler.interval_minutes} minutes. Press Ctrl+C to stop.")

    try:
        signal.pause()
    except AttributeError:
        import threading
        lock = threading.Event()
        lock.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobHunterRD - Buscador de empleo IT")
    parser.add_argument("--once", action="store_true", help="Ejecutar un solo ciclo y salir")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_scheduler()
