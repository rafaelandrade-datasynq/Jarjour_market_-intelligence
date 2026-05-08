from market.models import ConfidenceStatus, Listing, RawListing, SearchRun


def recalculate_search_run_totals(search_run: SearchRun) -> SearchRun:
    listings = Listing.objects.filter(raw_listing__search_run=search_run)

    search_run.total_raw_collected = RawListing.objects.filter(search_run=search_run).count()
    search_run.total_normalized = listings.exclude(confidence_status=ConfidenceStatus.RAW).count()
    search_run.total_reliable = listings.filter(confidence_status=ConfidenceStatus.RELIABLE).count()
    search_run.total_review = listings.filter(confidence_status=ConfidenceStatus.REVIEW).count()
    search_run.total_incomplete = listings.filter(
        confidence_status=ConfidenceStatus.INCOMPLETE
    ).count()
    search_run.total_probable_duplicates = listings.filter(
        confidence_status=ConfidenceStatus.PROBABLE_DUPLICATE
    ).count()
    search_run.total_discarded = listings.filter(
        confidence_status=ConfidenceStatus.DISCARDED
    ).count()
    search_run.total_opportunities = listings.filter(is_opportunity=True).count()
    search_run.save(
        update_fields=[
            "total_raw_collected",
            "total_normalized",
            "total_reliable",
            "total_review",
            "total_incomplete",
            "total_probable_duplicates",
            "total_discarded",
            "total_opportunities",
            "updated_at",
        ]
    )
    return search_run
