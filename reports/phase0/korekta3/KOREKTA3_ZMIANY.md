# FAZA 0 — korekta 3: raport zmian

Porównanie z audytowanym HEAD: `git diff --stat 6c633aa <commit korekty 3>`.
Poza repozytorium nie zmieniano niczego. Konfiguracja (`pyproject.toml`, Ruff, mypy, pytest) bez zmian.

| Plik | Zmiana | Podstawa |
|---|---|---|
| `src/market_intelligence/core/clock/utc.py` | `OverflowError` z `astimezone(UTC)` → `ValueError` z przyczyną; docstring | K2-A01 |
| `tests/regression/test_audit3_phase0.py` | **nowy**: regresje K2-A01, poprawne daty graniczne, wyłącznie `ValidationError` dla danych skrajnych | audyt 3 |
| `docs/DATA_CONTRACTS.md` | §1.3 daty bez odpowiednika UTC; §1.1 przechowanie `value_usdt` (56 cyfr) | K2-A01; audyt 3, ryzyko 3 |
| `docs/DECISIONS.md` | odnośniki do audytu 3 i korekty 3; OQ-16 | audyt 3 |
| `docs/MODULE_MAP.md`, `docs/TEST_PLAN.md` (§9), `CHANGELOG.md` | opis `ensure_utc`, nowe testy, wpis korekty 3 | — |
| `docs/PROJECT_STATE.md` | stan po korekcie 3 | — |
| `reports/phase0/audyt3/` | kopia raportu audytu 3 (SHA-256) | DEC-024 |
| `reports/phase0/korekta3/` | raport, testy, zmiany, logi | — |
