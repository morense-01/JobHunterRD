from dataclasses import dataclass, field
from typing import Optional

from app.models.job import Job


@dataclass
class FilterResult:
    passed: bool = True
    reason: str = ""
    rejected_by: str = ""


class FilterEngine:
    def __init__(
        self,
        provinces: list[str],
        positive_keywords: list[str],
        negative_keywords: list[str],
        excluded_companies: list[str],
    ) -> None:
        self._provinces = [p.strip().lower() for p in provinces]
        self._positive_keywords = [kw.strip().lower() for kw in positive_keywords]
        self._negative_keywords = [kw.strip().lower() for kw in negative_keywords]
        self._excluded_companies = [c.strip().lower() for c in excluded_companies]

    def evaluate(self, job: Job) -> FilterResult:
        result = self._check_excluded_company(job)
        if not result.passed:
            return result

        result = self._check_location(job)
        if not result.passed:
            return result

        result = self._check_negative_keywords(job)
        if not result.passed:
            return result

        result = self._check_positive_keywords(job)
        if not result.passed:
            return result

        return FilterResult(passed=True)

    def _check_excluded_company(self, job: Job) -> FilterResult:
        company_lower = job.company.strip().lower()
        for excluded in self._excluded_companies:
            if excluded in company_lower:
                return FilterResult(passed=False, reason=f"Empresa excluida: {job.company}", rejected_by="excluded_company")
        return FilterResult(passed=True)

    def _check_location(self, job: Job) -> FilterResult:
        if not self._provinces:
            return FilterResult(passed=True)

        location_lower = job.location.strip().lower() if job.location else ""
        if not location_lower:
            return FilterResult(passed=True)

        for province in self._provinces:
            if province in location_lower:
                return FilterResult(passed=True)

        return FilterResult(passed=False, reason=f"Ubicación no coincide: {job.location}", rejected_by="location")

    def _check_negative_keywords(self, job: Job) -> FilterResult:
        text_to_check = f"{job.title} {job.description}".lower()
        for keyword in self._negative_keywords:
            if keyword in text_to_check:
                return FilterResult(
                    passed=False,
                    reason=f"Palabra negativa detectada: {keyword}",
                    rejected_by="negative_keyword",
                )
        return FilterResult(passed=True)

    def _check_positive_keywords(self, job: Job) -> FilterResult:
        if not self._positive_keywords:
            return FilterResult(passed=False, reason="No hay palabras positivas configuradas", rejected_by="positive_keyword")

        text_to_check = f"{job.title} {job.description}".lower()
        for keyword in self._positive_keywords:
            if keyword in text_to_check:
                return FilterResult(passed=True)

        return FilterResult(passed=False, reason="No coincide con palabras positivas", rejected_by="positive_keyword")
