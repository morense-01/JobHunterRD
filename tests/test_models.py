from datetime import datetime

from app.models.enums import VacancyStatus, RemoteType
from app.models.job import Job


class TestVacancyStatus:
    def test_values(self) -> None:
        assert VacancyStatus.NEW == "Nueva"
        assert VacancyStatus.NOTIFIED == "Notificada"
        assert VacancyStatus.APPLIED == "Aplicada"
        assert VacancyStatus.IGNORED == "Ignorada"


class TestRemoteType:
    def test_values(self) -> None:
        assert RemoteType.ON_SITE == "Presencial"
        assert RemoteType.REMOTE == "Remoto"
        assert RemoteType.HYBRID == "Híbrido"


class TestJob:
    def test_create_job(self) -> None:
        job = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santo Domingo",
            remote=RemoteType.HYBRID,
            salary="80,000 DOP",
            description="Puesto gerencial de TI",
            url="https://example.com/job",
            portal="aldaba",
        )
        assert job.title == "Gerente TI"
        assert job.company == "Tech Corp"
        assert job.remote == RemoteType.HYBRID
        assert job.salary == "80,000 DOP"
        assert job.found_at is not None

    def test_job_defaults(self) -> None:
        job = Job(
            title="DevOps",
            company="Cloud Inc",
            location="Distrito Nacional",
            url="https://example.com/devops",
            portal="linkedin",
        )
        assert job.remote == RemoteType.UNKNOWN
        assert job.salary is None
        assert job.description == ""
        assert job.publication_date is None

    def test_job_with_publication_date(self) -> None:
        pub_date = datetime(2026, 7, 10)
        job = Job(
            title="Cloud Architect",
            company="AWS Dominicana",
            location="Santo Domingo Oeste",
            url="https://example.com/architect",
            portal="computrabajo",
            publication_date=pub_date,
        )
        assert job.publication_date == pub_date
