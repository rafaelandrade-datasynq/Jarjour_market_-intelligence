# Data Visibility Gate

Collected data cannot disappear from the dashboard, summary or collection totals just because it did not pass validation.

The product rule is:

`Coletado != Validado != Oportunidade`

Validation may classify a listing as reliable, review, incomplete, probable duplicate or discarded. It must not silently remove the raw record from the historical base.

The dashboard must always communicate the raw collected universe alongside filtered or trusted views. If a user sees only reliable records, the UI or summary must still explain how many raw records were collected.

`RawListing` rows without an associated `Listing` must remain visible in summary and dashboard totals as raw items pending normalization.

The quality gate checks that `market_summary.total_raw_collected` matches the number of persisted `RawListing` rows and that `market_summary.total_raw_without_listing` matches raw rows still missing a normalized `Listing`.

The gate must fail when `RawListing` rows without `Listing` exist and `total_raw_without_listing` is absent, hidden or under-reported in the summary.

Local caches are operational artifacts, not data visibility evidence. They should be cleaned with `python scripts/clean_workspace.py`, but ignored local caches do not block release if they are not versioned and any Windows permission failure is documented.
