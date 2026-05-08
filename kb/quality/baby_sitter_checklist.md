# BabySitter Checklist

The BabySitter Agent reviews each delivery as a fiscalizer.

Checklist:

- Read `kb/INDEX.md` and the relevant product, data contract and quality docs.
- Confirm the implementation matches the ticket scope.
- Confirm no real scraping was added unless the ticket asked for it.
- For offline-first scraping, confirm tests use saved HTML fixtures only and do not access real portals or live browsers.
- Confirm scraper tests use the official fixture in `packages/scrapers/fixtures/dfimoveis_search_results_sample.html`, not a divergent smaller copy.
- Confirm the official offline fixture has at least 8 representative candidates and preserves incomplete rows.
- Confirm every collected record is saved as `RawListing`.
- Confirm scraper output does not create `Listing` directly.
- Confirm normalization creates `Listing` from `RawListing` without deleting `RawListing`.
- Confirm normalization does not mark `is_opportunity=True` automatically.
- Confirm incomplete normalized records remain visible as `REVIEW` or `INCOMPLETE`.
- Confirm validation classifies records instead of hiding them.
- Confirm dashboard or summary shows total raw collected.
- Confirm `RawListing` rows without `Listing` appear in summary/dashboard and that the Data Visibility Gate fails if they are hidden.
- Confirm brand refinements do not remove required visibility cards or the raw-without-normalization alert.
- Confirm dashboard copy feels executive and useful for Carol, not like a technical scraping console.
- Confirm charts are absent or clearly useful; unnecessary visual noise should be rejected.
- Confirm Excel headers match `kb/data_contracts/excel_export_contract.md`.
- Confirm the Carol workbook has `Pesquisa Carol`, `Oportunidades`, `Revisar`, `Links` and `Resumo da Coleta`.
- Confirm `Resumo da Coleta` shows raw totals and `Brutos sem normalização`, so raw records without `Listing` are not hidden by the export.
- Confirm records for review remain visible in the `Revisar` tab.
- Confirm manual review creates `ListingReview`.
- Confirm rejecting a listing does not delete `Listing` or `RawListing`.
- Confirm `confidence_status`, `review_status` and `is_opportunity` remain separate concepts.
- Confirm offline scraper quality gate validates at least 8 parsed candidates, RawListing-only persistence, raw-without-listing visibility and no live portal access code.
- Confirm live preflight is disabled by default and dry-run is default.
- Confirm live preflight tests do not open a browser or access the internet.
- Confirm live preflight has strict limits and saves evidence.
- Confirm live preflight does not create `Listing`, call normalization or mark opportunities.
- Confirm no proxy, CAPTCHA bypass, login, paywall bypass, user-agent rotation or evasion was introduced.
- Confirm tests cover the requested behavior.
- Confirm `make verify` was run or the blocker is documented.
- Confirm local caches and generated artifacts are ignored and can be cleaned with `python scripts/clean_workspace.py`. Ignored local caches do not block release if they are not versioned and permission failures are documented.
- List any contract changes that require KB updates.
