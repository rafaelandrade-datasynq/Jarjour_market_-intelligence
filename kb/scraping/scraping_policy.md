# Scraping Policy

Real portal scraping is not implemented in the offline-first scraper ticket.

Ticket 5 permits Playwright as a future dependency and local fixture parsing only. Tests and scripts must not access DF Imoveis, Wimoveis or any real portal.

The official offline fixture is `packages/scrapers/fixtures/dfimoveis_search_results_sample.html`. It must contain at least 8 fake representative candidates. Tests and quality gates must use this fixture and fail if the parser returns fewer than 8 candidates.

Future Playwright collection must:

- respect source terms and legal guidance;
- capture raw listings before validation;
- store evidence pointers when possible;
- mark source name and captured timestamp;
- never silently drop raw records because parsing failed.

Offline-first parser rules:

- read saved HTML fixtures;
- never make HTTP requests to real portals;
- never launch a live browser in tests;
- persist scraper output as `RawListing`;
- never create `Listing` directly from scraper output;
- preserve incomplete candidates as raw records instead of dropping them.

## Live Preflight Rules

Live scraping preflight is disabled by default. It may run only when `ENABLE_LIVE_SCRAPING=true`, and dry-run remains the default mode.

The initial preflight limits are:

- max pages: 1
- max candidates: 20
- timeout: 30 seconds

The preflight is not seasonal collection, not production, and not a complete market read. Small results must be marked incomplete/preflight and never presented as market coverage.

Live preflight must not use login, proxy, CAPTCHA bypass, paywall bypass, user-agent rotation or evasion. If a block, CAPTCHA or login wall appears, the system must save evidence and stop gracefully.

Live scraper output must be persisted as `RawListing` only when dry-run is off. It must never create `Listing`, call normalization, mark opportunity or review records automatically.
