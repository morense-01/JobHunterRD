from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class SchedulerManager:
    def __init__(self, interval_minutes: int, job_func: Callable) -> None:
        self._interval = interval_minutes
        self._job_func = job_func
        self._scheduler = BackgroundScheduler()

    def start(self) -> None:
        self._scheduler.add_job(
            self._job_func,
            "interval",
            minutes=self._interval,
            id="job_hunter",
            name="JobHunterRD: busqueda de vacantes",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info(f"Scheduler started. Interval: every {self._interval} minutes.")

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped.")
