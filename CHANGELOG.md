# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/). Wersje pakietu wg
`pyproject.toml`; wersja schematu danych wg `SCHEMA_VERSION` (docs/DATA_CONTRACTS.md).

## [Unreleased]

## [0.0.1] — 2026-10-22 — FAZA 0
### Dodano
- Struktura repozytorium `src/` (modularny monolit), `pyproject.toml` z przypiętymi wersjami
  zależności, `requirements-dev.lock` (constraints), `.gitignore`, `.gitattributes`, `.env.example`.
- Kontrakty danych, schemat w wersji **1**: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) w `market_intelligence.core.models`.
- Prymityw `ensure_utc` w `market_intelligence.core.clock`.
- Zarezerwowane, puste pakiety `core.config` i `core.events` (DEC-008).
- Testy jednostkowe i kontraktowe (pytest), syntetyczne fixture'y JSON.
- Konfiguracja Ruff (lint + format) i mypy (strict, plugin Pydantic).
- Dokumentacja niezależna od agenta AI: AGENTS.md, CLAUDE.md, `.github/copilot-instructions.md`, `docs/*`.
- Raporty FAZY 0 w `reports/phase0/`.
