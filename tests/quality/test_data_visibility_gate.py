from market.models import Listing, RawListing, ReviewStatus, SearchRun
from market.services.review import review_listing

from packages.quality_gates.data_visibility_gate import (
    run_data_visibility_gate,
    validate_data_visibility_summary,
)
from packages.quality_gates.review_flow_gate import run_review_flow_gate


def test_data_visibility_gate_keeps_raw_total_visible(demo_run):
    assert RawListing.objects.count() == demo_run.total_raw_collected
    result = run_data_visibility_gate()
    assert result.passed, result.message


def test_data_visibility_gate_accepts_visible_raw_without_listing(db):
    run = SearchRun.objects.create(source_name="quality")
    raw_with_listing = RawListing.objects.create(
        search_run=run,
        source_name="quality",
        raw_title="Normalizado",
    )
    RawListing.objects.create(search_run=run, source_name="quality", raw_title="Pendente")
    Listing.objects.create(raw_listing=raw_with_listing, source_name="quality")

    result = run_data_visibility_gate()

    assert result.passed, result.message


def test_data_visibility_gate_rejects_hidden_raw_without_listing(db):
    run = SearchRun.objects.create(source_name="quality")
    raw_with_listing = RawListing.objects.create(
        search_run=run,
        source_name="quality",
        raw_title="Normalizado",
    )
    RawListing.objects.create(search_run=run, source_name="quality", raw_title="Pendente")
    Listing.objects.create(raw_listing=raw_with_listing, source_name="quality")

    raw_total = RawListing.objects.count()
    raw_without_listing = RawListing.objects.filter(listing__isnull=True).count()
    hidden_summary = {"total_raw_collected": raw_total}
    incorrect_summary = {
        "total_raw_collected": raw_total,
        "total_raw_without_listing": 0,
    }

    missing_errors = validate_data_visibility_summary(
        hidden_summary,
        raw_total=raw_total,
        raw_without_listing=raw_without_listing,
    )
    incorrect_errors = validate_data_visibility_summary(
        incorrect_summary,
        raw_total=raw_total,
        raw_without_listing=raw_without_listing,
    )

    assert raw_without_listing == 1
    assert any("total_raw_without_listing" in error for error in missing_errors)
    assert any("total_raw_without_listing" in error for error in incorrect_errors)


def test_review_flow_gate_accepts_review_that_preserves_raw_listing(db):
    run = SearchRun.objects.create(source_name="quality")
    raw = RawListing.objects.create(search_run=run, source_name="quality", raw_title="Sala")
    listing = Listing.objects.create(raw_listing=raw, source_name="quality")

    review_listing(listing, ReviewStatus.REJECTED)

    result = run_review_flow_gate()

    assert result.passed, result.message
