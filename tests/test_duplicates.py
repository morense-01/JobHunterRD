from app.utils.hasher import HashGenerator


class TestHashGenerator:
    def test_same_input_produces_same_hash(self) -> None:
        h1 = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo")
        h2 = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo")
        assert h1 == h2

    def test_different_input_produces_different_hash(self) -> None:
        h1 = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo")
        h2 = HashGenerator.generate("Tech Corp", "DevOps", "Santo Domingo")
        assert h1 != h2

    def test_case_insensitive(self) -> None:
        h1 = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo Oeste")
        h2 = HashGenerator.generate("tech corp", "gerente ti", "santo domingo oeste")
        assert h1 == h2

    def test_whitespace_insensitive(self) -> None:
        h1 = HashGenerator.generate("  Tech Corp  ", "Gerente TI", "Santo Domingo")
        h2 = HashGenerator.generate("Tech Corp", "  Gerente TI  ", "  Santo Domingo  ")
        assert h1 == h2

    def test_different_company_different_hash(self) -> None:
        h1 = HashGenerator.generate("Company A", "Gerente TI", "Santo Domingo")
        h2 = HashGenerator.generate("Company B", "Gerente TI", "Santo Domingo")
        assert h1 != h2

    def test_different_location_different_hash(self) -> None:
        h1 = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo")
        h2 = HashGenerator.generate("Tech Corp", "Gerente TI", "Distrito Nacional")
        assert h1 != h2

    def test_hash_length(self) -> None:
        h = HashGenerator.generate("Tech Corp", "Gerente TI", "Santo Domingo")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
