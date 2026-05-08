# Listing Schema

## SearchRun

Represents one collection or import run. It stores source, filters, lifecycle status and the totals that keep the raw universe visible:

- total raw collected
- total normalized
- total reliable
- total review
- total incomplete
- total probable duplicates
- total discarded
- total opportunities

## RawListing

Stores every collected item before validation. `RawListing` is append-only by policy for collected source evidence. It includes raw title, description, address, price, area, condominium, contact, phone, source URL and raw JSON payload.

If a `RawListing` does not yet have an associated `Listing`, it is still part of the collected universe. Summaries and dashboards must expose this as raw data pending normalization.

Offline scraper output must be persisted here first. Scrapers must not create `Listing` directly; normalization is a separate future step.

## Listing

Represents a normalized business-facing listing derived from a raw listing. It stores address, neighborhood, type, purpose, area, rent, rent per square meter, condominium, contact, notes, confidence status, review status and opportunity score. A missing `Listing` must not be treated as a discarded `RawListing`.

`confidence_status` is the data-confidence classification. `review_status` is Carol or team manual review. Rejection updates review status; it must not delete the listing or its raw source row. Opportunity is a commercial mark through `is_opportunity=True`, not a substitute for raw-data validation.

Normalization creates or updates `Listing` from `RawListing`. It may classify the resulting listing as `RELIABLE`, `REVIEW`, `INCOMPLETE` or `PROBABLE_DUPLICATE`, but it must not set review decisions or mark opportunity automatically. Incomplete raw rows still become traceable `Listing` rows when enough source identity exists to preserve them for review.

## PriceSnapshot

Stores observed price values over time for a listing.

## ListingReview

Stores Carol or team review decisions with comment, reviewer and timestamp. Each manual review action must create a `ListingReview` for auditability.

New fields require this document to be updated before code changes are finalized.
