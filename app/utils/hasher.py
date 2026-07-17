import hashlib


class HashGenerator:
    @staticmethod
    def generate(company: str, title: str, location: str) -> str:
        raw = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
