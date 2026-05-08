# Jarjour Market Intelligence

Jarjour Market Intelligence is an MVP for Carol's monthly real estate market research workflow. It replaces a manual spreadsheet process with a historical database, executive dashboard, confidence classification, opportunity ranking and Excel export in Carol's expected format.

## Architecture

- Backend: Python, Django, Django Ninja.
- Frontend: Django Templates, HTMX, Tailwind CSS.
- Database: SQLite in the MVP, structured to migrate to PostgreSQL later.
- Future scraping: Playwright with evidence capture and seasonal collection.
- Quality: pytest, ruff, Django checks and initial data quality gates.

Real scraping is not implemented in this ticket. The app uses realistic demo data to validate dashboard, API and Excel export behavior.

## Install

```bash
make install
make migrate
```

## Run Locally

```bash
make seed
make run
```

Open:

- Dashboard: `http://127.0.0.1:8000/dashboard/`
- API docs: `http://127.0.0.1:8000/api/v1/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Demo Data

```bash
make seed
```

This creates a demo `SearchRun`, raw listings, normalized listings, price snapshots and mixed confidence statuses.

## Excel Export

Download through:

- `http://127.0.0.1:8000/api/v1/exports/carol-xlsx`
- `http://127.0.0.1:8000/exports/carol-xlsx/`

Generate a dated file locally with:

```bash
python scripts/export_carol_xlsx.py
```

On Windows with the local virtual environment:

```powershell
.\venv\Scripts\python.exe scripts\export_carol_xlsx.py
```

The script saves the workbook in `data/exports/` with a name like `jarjour-pesquisa-carol-YYYYMMDD.xlsx`.

The workbook has the tabs `Pesquisa Carol`, `Oportunidades`, `Revisar`, `Links` and `Resumo da Coleta`. `Pesquisa Carol`, `Oportunidades` and `Revisar` use Carol's main columns plus traceability columns for status, capture date and source. `Resumo da Coleta` exists so raw totals, raw rows without normalization, discarded rows and review queues remain visible even when the property tabs are filtered.

No Excel tab or header may be removed or reordered without updating `kb/data_contracts/excel_export_contract.md` and the export tests.

## Tests And Verification

```bash
make test
make verify
make clean
```

`make verify` runs lint, tests, Django checks, migration drift check and quality gates.
`make clean` removes local Python, pytest, ruff, mypy, coverage, export and log artifacts that are not part of the product.

On Windows environments without GNU Make installed, run the equivalent local verifier:

```powershell
.\scripts\verify.ps1
```

The Windows verifier runs `scripts\clean_workspace.py` before and after the checks. Local ignored caches do not block a release when they are not versioned, but the cleanup script should make them repeatable and visible when Windows permissions prevent removal.

## Core Data Principle

Collected data is not the same as normalized data, normalized data is not human-reviewed data, and reviewed data is not automatically an opportunity.

Every collected item must be saved as `RawListing`. A `RawListing` is the preserved raw row from collection or import, including source URL, raw title, raw address, raw price and raw payload.

A `Listing` is the normalized business-facing record derived from a `RawListing`. It can have confidence status, review status, price per square meter and opportunity score.

`RawListing` without `Listing` cannot disappear. It means the item was collected but has not been normalized yet, so the summary and dashboard must still show it as part of the raw universe. The protected product rule is:

```text
Coletado != Normalizado != Revisado != Oportunidade
```

The Data Visibility Gate must fail if `RawListing` rows without `Listing` are omitted from summary totals.
The Excel export follows the same rule: records for review are not hidden, and raw records that have not become `Listing` rows are counted in `Resumo da Coleta` as `Brutos sem normalização`.

## Normalization

Normalize pending raw listings with:

```powershell
.\venv\Scripts\python.exe scripts\normalize_pending_raw_listings.py
```

The same workflow is available through `POST /api/v1/normalization/run` with optional `search_run_id` and `limit`.

Normalization parses money, area, condominium, text, neighborhood and property type into a `Listing`. It never deletes `RawListing`, never marks `is_opportunity=True`, and never records a human review decision. Incomplete rows still become `Listing` records with `confidence_status=REVIEW` or `INCOMPLETE`, so they remain visible for Carol.

## Manual Review

Carol can review normalized listings from the dashboard or API:

- `Aprovar` sets `review_status=APPROVED`.
- `Marcar para revisão` sets `review_status=NEEDS_REVIEW`.
- `Rejeitar` sets `review_status=REJECTED` without deleting `Listing` or `RawListing`.
- `Marcar como oportunidade` sets `review_status=OPPORTUNITY` and `is_opportunity=True`.

Each action creates a `ListingReview` with decision, comment, reviewer and timestamp. `confidence_status` remains the data-confidence classification; `review_status` is the human business decision. Opportunity is a commercial mark, not proof that raw data was technically validated.

## Offline Scraper Fixture

Ticket 5 introduces an offline-first scraper foundation. It does not access DF Imóveis, Wimóveis or any real portal.

Run the local fixture parser with:

```powershell
.\venv\Scripts\python.exe scripts\run_offline_scraper_fixture.py
```

The official offline fixture is `packages/scrapers/fixtures/dfimoveis_search_results_sample.html`. Tests and scripts must use that same fixture; there is no separate smaller test fixture. The fixture must keep at least 8 fake, representative candidates, including incomplete rows and a probable duplicate, so parser and persistence tests protect realistic raw-data visibility.

The script saves structured evidence in `data/evidence/dfimoveis/YYYYMMDD-HHMMSS/` with `page.html` and `meta.json`, creates a `SearchRun` and persists only `RawListing` rows. It never creates `Listing`; normalization is a future step. Incomplete candidates remain raw records and must not be discarded.

This preserves:

```text
Coletado != Normalizado != Revisado != Oportunidade
```

## Live Scraping Preflight

Live scraping is disabled by default and is not part of normal verification. The first live path is a controlled preflight only; it is not seasonal collection and must not be treated as a complete market read.

Safe defaults live in `.env.example`:

```text
ENABLE_LIVE_SCRAPING=false
LIVE_SCRAPING_DRY_RUN=true
LIVE_SCRAPING_MAX_PAGES=1
LIVE_SCRAPING_MAX_CANDIDATES=20
LIVE_SCRAPING_TIMEOUT_SECONDS=30
```

Run the preflight script only intentionally:

```powershell
.\venv\Scripts\python.exe scripts\run_live_scraper_preflight.py
```

With `ENABLE_LIVE_SCRAPING=false`, the script aborts before opening a browser. With dry-run enabled, it may capture/parse evidence but must not persist `RawListing`. Persistent mode, when explicitly enabled later, may create `RawListing` only. It must never create `Listing`, normalize automatically, mark opportunity, use login, proxy, CAPTCHA bypass or user-agent rotation.

Every live preflight capture must save evidence under `data/evidence/` with `page.html`, `meta.json` and `screenshot.png` when available. Small live results are preflight/incomplete evidence, not a complete view of the market.
