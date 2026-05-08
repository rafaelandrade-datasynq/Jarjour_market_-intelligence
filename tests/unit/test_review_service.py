import pytest
from market.models import Listing, ListingReview, RawListing, ReviewStatus, SearchRun
from market.services.review import review_listing
from market.services.totals import recalculate_search_run_totals


def _listing():
    run = SearchRun.objects.create(source_name="review")
    raw = RawListing.objects.create(search_run=run, source_name="review", raw_title="Sala")
    listing = Listing.objects.create(
        raw_listing=raw,
        source_name="review",
        endereco="SCS Quadra 2",
        bairro="Asa Sul",
        tipo_imovel="Sala",
        finalidade="Aluguel",
    )
    recalculate_search_run_totals(run)
    return run, raw, listing


def test_review_listing_approves_listing(db):
    _, _, listing = _listing()

    review = review_listing(listing, ReviewStatus.APPROVED, reviewed_by="Carol")

    listing.refresh_from_db()
    assert listing.review_status == ReviewStatus.APPROVED
    assert not listing.is_opportunity
    assert review.decision == ReviewStatus.APPROVED
    assert ListingReview.objects.count() == 1


def test_review_listing_marks_needs_review(db):
    _, _, listing = _listing()

    review = review_listing(listing, ReviewStatus.NEEDS_REVIEW, comment="Conferir contato")

    listing.refresh_from_db()
    assert listing.review_status == ReviewStatus.NEEDS_REVIEW
    assert review.comment == "Conferir contato"
    assert ListingReview.objects.count() == 1


def test_review_listing_rejects_without_deleting_listing_or_raw(db):
    run, raw, listing = _listing()
    raw_total_before = run.total_raw_collected

    review = review_listing(listing, ReviewStatus.REJECTED, reviewed_by="Carol")

    listing.refresh_from_db()
    run.refresh_from_db()
    assert listing.review_status == ReviewStatus.REJECTED
    assert Listing.objects.filter(id=listing.id).exists()
    assert RawListing.objects.filter(id=raw.id).exists()
    assert run.total_raw_collected == raw_total_before
    assert review.decision == ReviewStatus.REJECTED


def test_review_listing_marks_opportunity_and_recalculates_totals(db):
    run, _, listing = _listing()
    assert run.total_opportunities == 0

    review = review_listing(listing, ReviewStatus.OPPORTUNITY)

    listing.refresh_from_db()
    run.refresh_from_db()
    assert listing.review_status == ReviewStatus.OPPORTUNITY
    assert listing.is_opportunity
    assert run.total_opportunities == 1
    assert review.decision == ReviewStatus.OPPORTUNITY


def test_review_listing_rejects_invalid_decision(db):
    _, _, listing = _listing()

    with pytest.raises(ValueError, match="Decision invalid"):
        review_listing(listing, "INVALID")
