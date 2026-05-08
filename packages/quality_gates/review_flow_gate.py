from dataclasses import dataclass

from market.models import Listing, ListingReview, RawListing, ReviewStatus


@dataclass(frozen=True)
class ReviewFlowResult:
    passed: bool
    message: str


def run_review_flow_gate() -> ReviewFlowResult:
    review_count = ListingReview.objects.count()
    if review_count == 0:
        return ReviewFlowResult(True, "No manual reviews yet; review flow gate is neutral.")

    missing_listing = ListingReview.objects.filter(listing__isnull=True).exists()
    if missing_listing:
        return ReviewFlowResult(False, "Manual review without Listing found.")

    reviewed_listing_ids = ListingReview.objects.values_list("listing_id", flat=True).distinct()
    reviewed_listings = Listing.objects.filter(id__in=reviewed_listing_ids)
    if reviewed_listings.count() != len(set(reviewed_listing_ids)):
        return ReviewFlowResult(False, "A reviewed Listing was deleted.")

    reviewed_raw_ids = reviewed_listings.exclude(raw_listing__isnull=True).values_list(
        "raw_listing_id", flat=True
    )
    if RawListing.objects.filter(id__in=reviewed_raw_ids).count() != len(set(reviewed_raw_ids)):
        return ReviewFlowResult(False, "A reviewed RawListing was deleted.")

    rejected_reviews = ListingReview.objects.filter(decision=ReviewStatus.REJECTED)
    if rejected_reviews.exclude(listing__review_status=ReviewStatus.REJECTED).exists():
        return ReviewFlowResult(False, "Rejected review did not preserve REJECTED review_status.")

    opportunity_reviews = ListingReview.objects.filter(decision=ReviewStatus.OPPORTUNITY)
    if opportunity_reviews.exclude(listing__is_opportunity=True).exists():
        return ReviewFlowResult(False, "Opportunity review did not mark is_opportunity.")

    if reviewed_listings.filter(confidence_status__in=ReviewStatus.values).exists():
        return ReviewFlowResult(
            False,
            "confidence_status appears to contain review status values.",
        )

    return ReviewFlowResult(True, "Manual review flow preserves Listing and RawListing records.")
