# Quality Gates

Initial gates:

- lint with ruff;
- pytest;
- Django system check;
- data visibility gate;
- Excel contract gate;
- review flow gate;
- offline scraper fixture gate with at least 8 parsed candidates, RawListing-only persistence and no live portal access;
- normalization gate that creates Listing rows from RawListing without deleting raw data or marking opportunities automatically;
- live scraping safety gate that verifies disabled-by-default live mode, dry-run defaults, strict limits and no bypass patterns;
- anti-hallucination gate for unsupported live-scraping claims.

`make verify` is the mandatory final command.
