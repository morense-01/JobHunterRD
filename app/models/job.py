import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .enums import RemoteType


class Job(BaseModel):
    title: str
    company: str
    location: str
    remote: RemoteType = RemoteType.UNKNOWN
    salary: Optional[str] = None
    description: str = ""
    url: str
    portal: str
    publication_date: Optional[datetime] = None
    found_at: datetime = Field(default_factory=datetime.now)
    hash: str = ""

    @model_validator(mode="after")
    def _clean_fields(self) -> "Job":
        self.location = re.sub(
            r"hace\s+\d+\s+(días|día|horas|hora|semanas|semana|mes|meses).*$",
            "",
            self.location,
            flags=re.IGNORECASE,
        ).strip().rstrip(",").strip()
        self.company = self.company.strip()
        self.title = self.title.strip()
        return self
