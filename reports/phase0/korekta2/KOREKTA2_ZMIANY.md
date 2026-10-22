# FAZA 0 — korekta 2: raport zmian

Porównanie z audytowanym HEAD: `git diff --stat f0c36e9 <commit korekty 2>`.
Poza repozytorium nie zmieniano niczego.

| Plik | Zmiana | Podstawa |
|---|---|---|
| `src/market_intelligence/core/models/types.py` | lista dozwolonych zapisów czasu `_RFC3339`; poprawiona czarna lista `_NUMERIC_STRING`; `PositiveProductDecimal`, `MAX_PRODUCT_DECIMAL_PLACES`; fabryka `_financial_domain` | K1-01, DEC-004, DEC-020 |
| `src/market_intelligence/core/models/trade.py` | `value_usdt: PositiveProductDecimal`; opis dziedziny | DEC-020 |
| `src/market_intelligence/core/models/market_event.py` | docstring niezmiennika czasu | audyt 2 §8 |
| `tests/regression/test_audit2_phase0.py` | **nowy**: regresje K1-01, profil RFC 3339, dziedzina iloczynu | audyt 2 §4, §9 |
| `tests/regression/test_audit1_phase0.py` | nazwa i komentarz jednego testu (asercje bez zmian); stały identyfikator parametru `memoryview` (`_stable_id`) | DEC-020; deterministyczne ID testów |
| `tests/contracts/test_documentation.py` | wyszukiwanie odnośników pomija kod (w linii i bloki), zgodnie z semantyką Markdown — wzorzec `[.ffffff](Z\|…)` w kodzie był fałszywie zgłaszany jako link | fałszywe alarmy; uszkodzony odnośnik w zwykłym tekście nadal wykrywany (mutacja M11) |
| `docs/requirements/FAZA0_KOREKTA2_DECYZJE.md` | **nowy**: pytania i odpowiedzi użytkownika | DEC-024 |
| `docs/DECISIONS.md` | DEC-004, 005, 010, 020, 021, 022 → ACCEPTED; DEC-026; lista PROPOSED; OQ-14 | decyzje użytkownika |
| `docs/DATA_CONTRACTS.md` | §1.1 dziedziny (bez twierdzeń o pokryciu, OQ-14); §1.3 profil czasu; `PositiveProductDecimal`; historia schematu | audyt 2 §5, §8 |
| `docs/DEVELOPMENT.md` | §8.1 wyjątek DEC-026 | DEC-026 |
| `docs/MODULE_MAP.md`, `docs/TEST_PLAN.md`, `docs/EXCHANGE_API.md` | nowe typy, stałe, testy (§8), obowiązki konektorów | — |
| `docs/PROJECT_STATE.md`, `CHANGELOG.md` | stan po korekcie 2 | — |
| `reports/phase0/audyt2/` | kopia raportu audytu 2 (SHA-256) | DEC-024 |
| `reports/phase0/korekta2/` | raport, testy, zmiany, logi | — |

Konfiguracja (`pyproject.toml`, Ruff, mypy, pytest): **bez zmian**.
