from pathlib import Path

import pytest

from app.config.loader import ConfigLoader, Settings
from app.filters.engine import FilterEngine
from app.models.enums import RemoteType
from app.models.job import Job


@pytest.fixture
def sample_job() -> Job:
    return Job(
        title="Gerente de Tecnología",
        company="Empresa de Prueba",
        location="Santo Domingo Oeste",
        remote=RemoteType.ON_SITE,
        salary=None,
        description="Gestión de infraestructura TI, cloud y seguridad",
        url="https://example.com/job/1",
        portal="test",
    )


@pytest.fixture
def settings() -> Settings:
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        return ConfigLoader(str(config_path)).load()
    return Settings()


@pytest.fixture
def filter_engine(settings: Settings) -> FilterEngine:
    return FilterEngine(
        provinces=settings.provinces,
        positive_keywords=settings.positive_keywords,
        negative_keywords=settings.negative_keywords,
        excluded_companies=settings.excluded_companies,
    )
