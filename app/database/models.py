from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.models.enums import VacancyStatus


class Base(DeclarativeBase):
    pass


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal = Column(String(100), nullable=False)
    title = Column(String(300), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    remote = Column(String(50), nullable=True)
    salary = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False, unique=True)
    publication_date = Column(DateTime, nullable=True)
    found_at = Column(DateTime, default=datetime.now, nullable=False)
    hash = Column(String(64), nullable=False, unique=True)
    status = Column(SAEnum(VacancyStatus), default=VacancyStatus.NEW, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"<Vacancy(id={self.id}, title='{self.title}', company='{self.company}')>"


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_id = Column(Integer, nullable=False)
    status = Column(SAEnum(VacancyStatus), nullable=False)
    changed_at = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(Text, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_id = Column(Integer, nullable=False)
    channel = Column(String(50), nullable=False)
    sent_at = Column(DateTime, default=datetime.now, nullable=False)
    success = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
