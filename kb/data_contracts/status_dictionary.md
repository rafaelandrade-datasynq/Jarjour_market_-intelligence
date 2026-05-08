# Status Dictionary

## Confidence Status

Confidence status is the system's data-quality classification. It is not Carol's final business review.

- `RAW`: collected but not normalized.
- `NORMALIZED`: parsed into structured fields but not yet trusted.
- `RELIABLE`: enough fields and evidence to use confidently.
- `REVIEW`: needs human review.
- `INCOMPLETE`: missing important business fields.
- `PROBABLE_DUPLICATE`: likely repeats another listing.
- `DISCARDED`: retained for traceability but not useful for opportunity decisions.

Normalization assigns confidence status only. It does not approve, reject or mark opportunity. Missing rent should become `INCOMPLETE`; missing area, uncertain location or uncertain address should become `REVIEW` unless stronger duplicate evidence applies.

## Review Status

Review status is the human decision recorded during manual review. It must remain separate from confidence status.

- `NOT_REVIEWED`: no human decision yet.
- `APPROVED`: accepted for business use.
- `NEEDS_REVIEW`: requires Carol or team review.
- `REJECTED`: reviewed and rejected; this must not delete `Listing` or `RawListing`.
- `OPPORTUNITY`: selected as a business opportunity; this sets `is_opportunity=True` but does not prove raw data was technically validated.

`review_status` starts as `NOT_REVIEWED` when normalization creates a `Listing`. Only manual review flow should change it.
