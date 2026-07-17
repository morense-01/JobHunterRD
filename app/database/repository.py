from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.enums import VacancyStatus
from app.models.job import Job
from .models import Base, Vacancy, History, Notification


class DatabaseRepository:
    def __init__(self, db_path: str | Path) -> None:
        self._engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        return Session(self._engine, expire_on_commit=False)

    def vacancy_exists_by_hash(self, hash_value: str) -> bool:
        with self.get_session() as session:
            return session.query(Vacancy).filter(Vacancy.hash == hash_value).first() is not None

    def vacancy_exists_by_url(self, url: str) -> bool:
        with self.get_session() as session:
            return session.query(Vacancy).filter(Vacancy.url == url).first() is not None

    def save_job(self, job: Job) -> Optional[Vacancy]:
        if self.vacancy_exists_by_hash(job.hash):
            with self.get_session() as session:
                existing = session.query(Vacancy).filter(Vacancy.hash == job.hash).first()
                if existing:
                    existing.last_seen_at = datetime.now()
                    session.commit()
            return None

        vacancy = Vacancy(
            portal=job.portal,
            title=job.title,
            company=job.company,
            location=job.location,
            remote=job.remote.value,
            salary=job.salary,
            description=job.description,
            url=job.url,
            publication_date=job.publication_date,
            found_at=job.found_at,
            hash=job.hash,
            status=VacancyStatus.NEW,
            last_seen_at=datetime.now(),
        )

        with self.get_session() as session:
            session.add(vacancy)
            session.commit()
            session.refresh(vacancy)
            self._add_history_entry(session, vacancy.id, VacancyStatus.NEW, "Vacante encontrada")
            return vacancy

    def _add_history_entry(self, session: Session, vacancy_id: int, status: VacancyStatus, notes: str = "") -> None:
        entry = History(
            vacancy_id=vacancy_id,
            status=status,
            changed_at=datetime.now(),
            notes=notes,
        )
        session.add(entry)
        session.commit()

    def update_status(self, vacancy_id: int, new_status: VacancyStatus, notes: str = "") -> None:
        with self.get_session() as session:
            vacancy = session.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
            if vacancy:
                vacancy.status = new_status
                session.commit()
                self._add_history_entry(session, vacancy_id, new_status, notes)

    def get_new_vacancies(self) -> list[Vacancy]:
        with self.get_session() as session:
            return session.query(Vacancy).filter(Vacancy.status == VacancyStatus.NEW).all()

    def mark_as_notified(self, vacancy_id: int) -> None:
        self.update_status(vacancy_id, VacancyStatus.NOTIFIED, "Notificada por Telegram")

    def register_notification(self, vacancy_id: int, channel: str, success: bool, error: str = "") -> None:
        with self.get_session() as session:
            notif = Notification(
                vacancy_id=vacancy_id,
                channel=channel,
                sent_at=datetime.now(),
                success=1 if success else 0,
                error_message=error if not success else None,
            )
            session.add(notif)
            session.commit()

    def count_vacancies_by_portal(self) -> dict[str, int]:
        with self.get_session() as session:
            rows = session.query(Vacancy.portal).all()
            counts: dict[str, int] = {}
            for (portal,) in rows:
                counts[portal] = counts.get(portal, 0) + 1
            return counts
