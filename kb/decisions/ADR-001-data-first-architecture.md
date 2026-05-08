# ADR-001: Data-First Architecture

## Status

Accepted.

## Decision

The dashboard consults the historical database, not live scraping results. Collection, import, validation, review, scoring and export are separate steps.

## Rationale

Carol needs monthly market intelligence, auditability and history. A live-only search interface would repeat the manual process and lose institutional memory.

## Consequences

`RawListing`, `Listing`, `PriceSnapshot`, `ListingReview` and `SearchRun` are first-class models. Future scraping jobs must write to the database before downstream validation or dashboard use.
