# Jarjour Market Intelligence - Agent Guide

## Project Vision

Jarjour Market Intelligence is a Simple, Lovable, Complete application for Carol, an intermediary at Jarjour, to replace monthly manual real estate market research spreadsheets with a historical, auditable and executive workflow.

The MVP uses Django, Django Ninja, Django Templates, HTMX, Tailwind CSS and SQLite. It does not use Streamlit, React, UiPath or real portal scraping in this ticket.

## Mandatory Commands

- Install dependencies: `make install`
- Apply database migrations: `make migrate`
- Generate demo data: `make seed`
- Run locally: `make run`
- Run tests: `make test`
- Run lint: `make lint`
- Clean local artifacts: `make clean`
- Final verification before handoff: `make verify`

Every delivery must end with `make verify` unless there is a documented blocker.

## How To Read The KB

1. Start with `kb/INDEX.md`.
2. Identify the product, data contract, scraping, quality and decision documents relevant to the ticket.
3. Use the KB as the source of truth for data contracts and product rules.
4. Cite in the final summary which KB files were used.

## Data Rules

Do not invent fields. If a new field is needed, update the relevant KB data contract before changing code.

Never hide raw data. The core rule is:

`Coletado != Validado != Oportunidade`

For normalization tickets, use the stricter operational rule:

`Coletado != Normalizado != Revisado != Oportunidade`

Every collected row must be stored as `RawListing`. Validation classifies confidence and review status; it must not silently delete or hide records. Any dashboard, endpoint or export that shows filtered data must preserve visibility of the raw collected universe. `RawListing` rows without associated `Listing` rows must remain visible in summary and dashboard totals.

Normalization may create or update `Listing` rows from `RawListing`, but it must never delete raw data, never mark opportunity automatically and never write human review decisions. Incomplete normalized listings stay visible with `REVIEW` or `INCOMPLETE` confidence status.

The Data Visibility Gate must fail if `RawListing` rows without `Listing` are omitted or under-reported in summary totals.

Manual review must create `ListingReview` records. Rejection is a review decision, not deletion: never delete `Listing` or `RawListing` to represent a rejected property. Opportunity is an explicit business mark and must not be confused with raw collection or technical validation.

Do not change data contracts without updating:

- `kb/data_contracts/listing_schema.md`
- `kb/data_contracts/excel_export_contract.md`
- `kb/data_contracts/status_dictionary.md`
- relevant ADRs when architectural intent changes

The Carol Excel export contract is protected by KB and tests. Do not remove, rename or reorder workbook tabs or headers without updating `kb/data_contracts/excel_export_contract.md`, tests and the Excel quality gate. Export tabs for review and summary counts must not hide raw or reviewable records.

## Scraping Rule

Do not implement real portal scraping without a specific ticket. Ticket 5 only permits offline-first scraping foundations: parse the official saved fixture HTML, save evidence, persist `RawListing`, and never create `Listing` directly. Do not access DF Imóveis, Wimóveis or any portal in tests or scripts for this stage.

The official scraper fixture is `packages/scrapers/fixtures/dfimoveis_search_results_sample.html`. It must contain at least 8 fake representative candidates, including incomplete rows. Tests and quality gates must fail if the parser returns fewer than 8 candidates or if scraper persistence creates `Listing` rows.

Live scraping preflight is disabled by default and may only run when `ENABLE_LIVE_SCRAPING=true`. Dry-run is the default. Preflight is not broad seasonal collection and must never be represented as the complete market. Any block, login wall or CAPTCHA must be recorded as evidence and not bypassed. Live scraping may persist `RawListing` only; normalization and opportunity review remain separate later steps.

## BabySitter Agent

Use `kb/quality/baby_sitter_checklist.md` and `kb/prompts/babysitter_agent.md` to review each delivery. The BabySitter must verify that raw listings remain visible, tests cover acceptance criteria and no unsupported real-data or live-scraping claims were introduced.

Local caches such as `.ruff_cache`, `.pytest_cache`, `.mypy_cache`, `__pycache__`, `pytest-cache-files-*`, coverage output and generated exports are not product artifacts. They should be ignored by git and cleaned with `make clean` or `python scripts/clean_workspace.py`; ignored local caches do not block release if they are not versioned and any permission blocker is documented.

## Acceptance Criteria

- Monorepo structure exists.
- KB is created and useful.
- Django runs.
- Django Ninja exposes the initial endpoints.
- `/dashboard` opens with executive language and filters.
- Demo data can be generated.
- Carol Excel export exists and its headers are tested.
- Quality gates exist.
- Tests run before final handoff.
- Final handoff lists files created, commands run, tests created, KB files used and recommended next steps.

## Agent Behavior

Implement only the requested ticket. Do not widen scope into live scraping, external integrations, Docker, React or Streamlit. Before finishing, run tests and `make verify`, then summarize concrete outcomes and remaining risks.
