from dataclasses import dataclass

from market.models import RawListing
from market.selectors.summary import market_summary


@dataclass(frozen=True)
class DataVisibilityResult:
    passed: bool
    message: str


def validate_data_visibility_summary(
    summary: dict,
    *,
    raw_total: int,
    raw_without_listing: int,
) -> list[str]:
    errors = []
    if raw_total == 0:
        return errors
    if summary.get("total_raw_collected") != raw_total:
        errors.append(
            "Raw universe is hidden: summary total_raw_collected="
            f"{summary.get('total_raw_collected')}, RawListing rows={raw_total}."
        )
    if summary.get("total_raw_without_listing") != raw_without_listing:
        errors.append(
            "Raw listings without normalization are hidden: summary total_raw_without_listing="
            f"{summary.get('total_raw_without_listing')}, expected={raw_without_listing}."
        )
    return errors


def run_data_visibility_gate() -> DataVisibilityResult:
    raw_total = RawListing.objects.count()
    raw_without_listing = RawListing.objects.filter(listing__isnull=True).count()
    summary = market_summary()
    if raw_total == 0:
        return DataVisibilityResult(True, "No raw listings yet; gate is neutral.")
    errors = validate_data_visibility_summary(
        summary,
        raw_total=raw_total,
        raw_without_listing=raw_without_listing,
    )
    if errors:
        return DataVisibilityResult(False, " ".join(errors))
    return DataVisibilityResult(True, "Raw collected universe is visible in summary totals.")
