from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

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
