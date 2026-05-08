from django.db import transaction

from market.models import Listing, ListingReview, ReviewStatus
from market.services.totals import recalculate_search_run_totals

ALLOWED_REVIEW_DECISIONS = {
    ReviewStatus.APPROVED,
    ReviewStatus.NEEDS_REVIEW,
    ReviewStatus.REJECTED,
    ReviewStatus.OPPORTUNITY,
}


@transaction.atomic
def review_listing(
    listing: Listing,
    decision: str,
    comment: str = "",
    reviewed_by: str = "Carol",
) -> ListingReview:
    if decision not in ALLOWED_REVIEW_DECISIONS:
        allowed = ", ".join(sorted(ALLOWED_REVIEW_DECISIONS))
        raise ValueError(f"Decision invalid. Use one of: {allowed}.")

    listing.review_status = decision
    if decision == ReviewStatus.OPPORTUNITY:
        listing.is_opportunity = True

    listing.save(update_fields=["review_status", "is_opportunity", "updated_at"])

    review = ListingReview.objects.create(
        listing=listing,
        decision=decision,
        comment=comment,
        reviewed_by=reviewed_by or "Carol",
    )

    if listing.raw_listing_id:
        recalculate_search_run_totals(listing.raw_listing.search_run)

    return review
