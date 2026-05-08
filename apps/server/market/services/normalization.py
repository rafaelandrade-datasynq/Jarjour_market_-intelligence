from collections import Counter
from dataclasses import asdict

from django.db import transaction

from market.models import ConfidenceStatus, Listing, RawListing, ReviewStatus, SearchRun
from market.services.totals import recalculate_search_run_totals
from packages.normalizers.listing_normalizer import normalize_raw_listing


def normalize_raw_listing_to_listing(raw_listing: RawListing) -> Listing:
    data = normalize_raw_listing(raw_listing)
    values = asdict(data)
    values["confidence_status"] = _duplicate_aware_status(raw_listing, values)

    create_values = {
        **values,
        "review_status": ReviewStatus.NOT_REVIEWED,
        "is_opportunity": False,
        "opportunity_score": data.opportunity_score,
    }
    update_values = {
        key: value
        for key, value in values.items()
        if key not in {"review_status", "is_opportunity", "opportunity_score"}
    }
    listing, created = Listing.objects.update_or_create(
        raw_listing=raw_listing,
        defaults=create_values if not hasattr(raw_listing, "listing") else update_values,
    )
    listing._normalization_created = created
    return listing


@transaction.atomic
def normalize_search_run(search_run: SearchRun) -> dict:
    raw_listings = RawListing.objects.filter(search_run=search_run).order_by("id")
    return _normalize_raw_queryset(raw_listings, search_run=search_run)


@transaction.atomic
def normalize_pending_raw_listings(limit: int | None = None) -> dict:
    raw_listings = RawListing.objects.filter(listing__isnull=True).order_by("id")
    if limit is not None:
        raw_listings = raw_listings[:limit]
    return _normalize_raw_queryset(raw_listings)


def _normalize_raw_queryset(raw_listings, search_run: SearchRun | None = None) -> dict:
    processed = 0
    created = 0
    updated = 0
    statuses: Counter[str] = Counter()
    affected_runs: set[int] = set()

    for raw_listing in raw_listings:
        processed += 1
        listing = normalize_raw_listing_to_listing(raw_listing)
        if getattr(listing, "_normalization_created", False):
            created += 1
        else:
            updated += 1
        statuses[listing.confidence_status] += 1
        affected_runs.add(raw_listing.search_run_id)

    if search_run is not None:
        affected_runs.add(search_run.id)
    for run in SearchRun.objects.filter(id__in=affected_runs):
        recalculate_search_run_totals(run)

    return {
        "raw_processed": processed,
        "listings_created": created,
        "listings_updated": updated,
        "reliable": statuses[ConfidenceStatus.RELIABLE],
        "review": statuses[ConfidenceStatus.REVIEW],
        "incomplete": statuses[ConfidenceStatus.INCOMPLETE],
        "probable_duplicates": statuses[ConfidenceStatus.PROBABLE_DUPLICATE],
    }


def _duplicate_aware_status(raw_listing: RawListing, values: dict) -> str:
    duplicate_queryset = Listing.objects.filter(raw_listing__search_run=raw_listing.search_run)
    if raw_listing.pk:
        duplicate_queryset = duplicate_queryset.exclude(raw_listing=raw_listing)

    if (
        raw_listing.source_url
        and duplicate_queryset.filter(source_url=raw_listing.source_url).exists()
    ):
        return ConfidenceStatus.PROBABLE_DUPLICATE

    key_filters = {
        "endereco": values["endereco"],
        "aluguel": values["aluguel"],
        "area_m2": values["area_m2"],
    }
    if values["endereco"] and values["aluguel"] is not None and values["area_m2"] is not None:
        if duplicate_queryset.filter(**key_filters).exists():
            return ConfidenceStatus.PROBABLE_DUPLICATE

    return values["confidence_status"]
