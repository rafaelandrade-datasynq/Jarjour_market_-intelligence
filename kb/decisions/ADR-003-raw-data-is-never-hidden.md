# ADR-003: Raw Data Is Never Hidden

## Status

Accepted.

## Decision

`RawListing` is the traceable source for every collected record and must never be deleted automatically because validation failed.

## Rationale

The previous failure mode was hiding collected data when it did not pass validation. That makes the system look cleaner while destroying trust and auditability.

The product rule is:

`Coletado != Validado != Oportunidade`

## Consequences

The dashboard must show raw collection totals. Validation produces confidence classifications, not silent exclusions. Discarded and incomplete records remain visible in counts and traceable in the database.

`RawListing` rows without associated `Listing` rows must remain visible in summary and dashboard totals as raw items pending normalization. They are preserved records, not discarded records.
