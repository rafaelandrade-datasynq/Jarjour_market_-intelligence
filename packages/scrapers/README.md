# Scrapers

This package contains the offline-first scraping foundation.

Ticket 5 parses saved fixture HTML only. It does not access real portals, launch live browsers in tests, bypass CAPTCHA, use login, proxy or user-agent rotation, or create normalized `Listing` rows.

The official fixture is `packages/scrapers/fixtures/dfimoveis_search_results_sample.html`. It must contain at least 8 fake representative candidates and is the only fixture used by scraper tests and the offline runner.

Scraper output must be persisted as `RawListing` first. Normalization is a separate future step.
