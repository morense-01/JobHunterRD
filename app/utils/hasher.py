import hashlib
import re


class HashGenerator:
    @staticmethod
    def generate(company: str, title: str, location: str) -> str:
        clean_location = HashGenerator._clean_location(location)
        raw = f"{company.strip().lower()}|{title.strip().lower()}|{clean_location.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _clean_location(location: str) -> str:
        cleaned = re.sub(r"hace\s+\d+\s+(días|día|horas|hora|semanas|semana|mes|meses)", "", location, flags=re.IGNORECASE)
        cleaned = re.sub(r"\d+\s*(días|día|horas|hora|semanas|semana|mes|meses)\s*(ago|atrás)?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"·", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
