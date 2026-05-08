from decimal import Decimal

from django.db.models import Avg, Count, Q

from market.models import ConfidenceStatus, Listing, RawListing


def market_summary() -> dict:
    counts = Listing.objects.aggregate(
        total_normalized=Count("id", filter=~Q(confidence_status=ConfidenceStatus.RAW)),
        total_reliable=Count("id", filter=Q(confidence_status=ConfidenceStatus.RELIABLE)),
        total_review=Count("id", filter=Q(confidence_status=ConfidenceStatus.REVIEW)),
        total_incomplete=Count("id", filter=Q(confidence_status=ConfidenceStatus.INCOMPLETE)),
        total_probable_duplicates=Count(
            "id", filter=Q(confidence_status=ConfidenceStatus.PROBABLE_DUPLICATE)
        ),
        total_discarded=Count("id", filter=Q(confidence_status=ConfidenceStatus.DISCARDED)),
        total_opportunities=Count("id", filter=Q(is_opportunity=True)),
        average_rent_m2=Avg("aluguel_m2", filter=Q(aluguel_m2__isnull=False)),
    )
    counts["total_raw_collected"] = RawListing.objects.count()
    counts["total_raw_without_listing"] = RawListing.objects.filter(listing__isnull=True).count()
    if counts["average_rent_m2"] is not None:
        counts["average_rent_m2"] = Decimal(counts["average_rent_m2"]).quantize(Decimal("0.01"))
    return counts
