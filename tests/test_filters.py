import pytest

from app.filters.engine import FilterEngine
from app.models.enums import RemoteType
from app.models.job import Job


@pytest.fixture
def engine() -> FilterEngine:
    return FilterEngine(
        provinces=["santo domingo oeste", "distrito nacional"],
        positive_keywords=["gerente ti", "cloud", "devops", "infrastructure manager"],
        negative_keywords=["help desk", "junior", "pasante", "call center"],
        excluded_companies=["unipago", "madeco"],
    )


class TestLocationFilter:
    def test_accepts_valid_location(self, engine: FilterEngine) -> None:
        job = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            url="https://x.com/job1",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is True

    def test_rejects_unknown_location(self, engine: FilterEngine) -> None:
        job = Job(
            title="Gerente TI",
            company="Tech Corp",
            location="Santiago",
            url="https://x.com/job2",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is False
        assert result.rejected_by == "location"


class TestExcludedCompanies:
    def test_rejects_excluded_company(self, engine: FilterEngine) -> None:
        job = Job(
            title="Gerente TI",
            company="UNIPAGO",
            location="Santo Domingo Oeste",
            url="https://x.com/job3",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is False
        assert result.rejected_by == "excluded_company"

    def test_accepts_non_excluded_company(self, engine: FilterEngine) -> None:
        job = Job(
            title="Gerente TI",
            company="Empresa Nueva",
            location="Santo Domingo Oeste",
            url="https://x.com/job4",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is True


class TestPositiveKeywords:
    def test_accepts_matching_title(self, engine: FilterEngine) -> None:
        job = Job(
            title="Infrastructure Manager",
            company="Tech Corp",
            location="Distrito Nacional",
            url="https://x.com/job5",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is True

    def test_accepts_matching_description(self, engine: FilterEngine) -> None:
        job = Job(
            title="Analista de Sistemas",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            description="Experiencia en cloud y devops",
            url="https://x.com/job6",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is True

    def test_rejects_no_match(self, engine: FilterEngine) -> None:
        job = Job(
            title="Recepcionista",
            company="Hotel",
            location="Santo Domingo Oeste",
            description="Atención al cliente",
            url="https://x.com/job7",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is False
        assert result.rejected_by == "positive_keyword"


class TestNegativeKeywords:
    def test_rejects_help_desk(self, engine: FilterEngine) -> None:
        job = Job(
            title="Help Desk Analyst",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            description="Soporte nivel 1",
            url="https://x.com/job8",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is False
        assert result.rejected_by == "negative_keyword"

    def test_rejects_junior(self, engine: FilterEngine) -> None:
        job = Job(
            title="Junior Developer",
            company="Tech Corp",
            location="Santo Domingo Oeste",
            description="Puesto para junior",
            url="https://x.com/job9",
            portal="test",
        )
        result = engine.evaluate(job)
        assert result.passed is False
