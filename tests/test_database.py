from pathlib import Path

import pytest

from app.database.repository import DatabaseRepository
from app.models.enums import RemoteType, VacancyStatus
from app.models.job import Job
from app.utils.hasher import HashGenerator


@pytest.fixture
def db_repo(tmp_path: Path) -> DatabaseRepository:
    db_path = tmp_path / "test_jobhunter.db"
    return DatabaseRepository(str(db_path))


class TestDatabaseRepository:
    def test_save_and_retrieve_job(self, db_repo: DatabaseRepository) -> None:
        job = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            remote=RemoteType.ON_SITE,
            url="https://example.com/job-db-1",
            portal="test",
        )
        job.hash = HashGenerator.generate(job.company, job.title, job.location)

        saved = db_repo.save_job(job)
        assert saved is not None
        assert saved.id is not None
        assert saved.title == "Gerente TI"
        assert saved.status == VacancyStatus.NEW

    def test_duplicate_hash_not_saved(self, db_repo: DatabaseRepository) -> None:
        job1 = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            url="https://example.com/job-db-2",
            portal="test",
        )
        job1.hash = HashGenerator.generate(job1.company, job1.title, job1.location)
        db_repo.save_job(job1)

        job2 = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            url="https://example.com/job-db-3",
            portal="test",
        )
        job2.hash = HashGenerator.generate(job2.company, job2.title, job2.location)
        result = db_repo.save_job(job2)
        assert result is None

    def test_vacancy_exists_by_hash(self, db_repo: DatabaseRepository) -> None:
        job = Job(
            title="DevOps Engineer",
            company="Cloud Inc",
            location="Distrito Nacional",
            url="https://example.com/job-db-4",
            portal="test",
        )
        job.hash = HashGenerator.generate(job.company, job.title, job.location)
        db_repo.save_job(job)

        assert db_repo.vacancy_exists_by_hash(job.hash) is True
        assert db_repo.vacancy_exists_by_hash("nonexistent") is False

    def test_get_new_vacancies(self, db_repo: DatabaseRepository) -> None:
        job = Job(
            title="Cloud Architect",
            company="AWS",
            location="Santo Domingo Oeste",
            url="https://example.com/job-db-5",
            portal="test",
        )
        job.hash = HashGenerator.generate(job.company, job.title, job.location)
        db_repo.save_job(job)

        new_vacancies = db_repo.get_new_vacancies()
        assert len(new_vacancies) == 1
        assert new_vacancies[0].title == "Cloud Architect"

    def test_update_status(self, db_repo: DatabaseRepository) -> None:
        job = Job(
            title="Network Engineer",
            company="Telco",
            location="Santo Domingo Oeste",
            url="https://example.com/job-db-6",
            portal="test",
        )
        job.hash = HashGenerator.generate(job.company, job.title, job.location)
        saved = db_repo.save_job(job)

        db_repo.update_status(saved.id, VacancyStatus.IGNORED, "No relevante")
        new_vacancies = db_repo.get_new_vacancies()
        assert len(new_vacancies) == 0

    def test_register_notification(self, db_repo: DatabaseRepository) -> None:
        job = Job(
            title="SAP Consultant",
            company="SAP SE",
            location="Distrito Nacional",
            url="https://example.com/job-db-7",
            portal="test",
        )
        job.hash = HashGenerator.generate(job.company, job.title, job.location)
        saved = db_repo.save_job(job)

        db_repo.register_notification(saved.id, "telegram", True)
        db_repo.register_notification(saved.id, "telegram", False, "Error de red")
