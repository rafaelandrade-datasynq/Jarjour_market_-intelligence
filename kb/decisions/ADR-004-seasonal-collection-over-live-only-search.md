# ADR-004: Seasonal Collection Over Live-Only Search

## Status

Accepted.

## Decision

The product is designed for seasonal broad collection runs, not only one-off live searches.

## Rationale

Carol's monthly workflow benefits from comparable historical snapshots and repeated market measurement. A seasonal collection model supports trend analysis and opportunity scoring.

## Consequences

`SearchRun` and `PriceSnapshot` are part of the MVP schema even before real scraping exists.

Offline-first scraper foundations may create `SearchRun` and `RawListing` from saved fixtures before any live seasonal collection is implemented. Live Playwright collection remains a future decision-bound step.

A controlled live preflight may be used to validate technical feasibility, but it is not seasonal collection and must not be presented as complete market coverage. It remains feature-flagged, dry-run by default, limited to one page and evidence-first.
