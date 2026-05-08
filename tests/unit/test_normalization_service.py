from decimal import Decimal

from market.models import ConfidenceStatus, Listing, RawListing, SearchRun
from market.selectors.summary import market_summary
from market.services.normalization import (
    normalize_pending_raw_listings,
    normalize_raw_listing_to_listing,
    normalize_search_run,
)

from packages.quality_gates.normalization_gate import (
    _validate_normalization_state,
    run_normalization_gate,
)
from scripts.normalize_pending_raw_listings import main as normalize_pending_script_main


def _raw(run, **overrides):
    data = {
        "search_run": run,
        "source_name": run.source_name,
        "source_url": "https://fixture.local/default",
        "raw_title": "Sala comercial para aluguel na Asa Sul",
        "raw_description": "Fixture de normalizacao.",
        "raw_address": "CLS 308 Bloco B, Asa Sul",
        "raw_price": "R$ 3.500,00",
        "raw_area": "45 m²",
        "raw_condominium": "R$ 500",
        "raw_contact": "Equipe",
        "raw_phone": "(61) 3000-0000",
    }
    data.update(overrides)
    return RawListing.objects.create(**data)


def test_normalize_complete_raw_listing_creates_reliable_listing(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    raw = _raw(run)

    listing = normalize_raw_listing_to_listing(raw)

    assert listing.raw_listing == raw
    assert listing.aluguel == Decimal("3500.00")
    assert listing.area_m2 == Decimal("45.00")
    assert listing.aluguel_m2 == Decimal("77.78")
    assert listing.confidence_status == ConfidenceStatus.RELIABLE
    assert listing.review_status == "NOT_REVIEWED"
    assert listing.is_opportunity is False
    assert RawListing.objects.filter(id=raw.id).exists()


def test_normalize_raw_without_condominium_does_not_fail(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Noroeste")
    raw = _raw(run, raw_condominium="", source_url="https://fixture.local/no-cond")

    listing = normalize_raw_listing_to_listing(raw)

    assert listing.condominio is None
    assert listing.confidence_status == ConfidenceStatus.RELIABLE


def test_normalize_raw_without_area_is_review_or_incomplete(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    raw = _raw(run, raw_area="", source_url="https://fixture.local/no-area")

    listing = normalize_raw_listing_to_listing(raw)

    assert listing.area_m2 is None
    assert listing.confidence_status in [ConfidenceStatus.REVIEW, ConfidenceStatus.INCOMPLETE]
    assert RawListing.objects.filter(id=raw.id).exists()


def test_normalize_raw_without_phone_preserves_listing(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Norte")
    raw = _raw(run, raw_phone="", source_url="https://fixture.local/no-phone")

    listing = normalize_raw_listing_to_listing(raw)

    assert listing.telefone == ""
    assert listing.confidence_status == ConfidenceStatus.RELIABLE


def test_normalize_raw_without_rent_is_incomplete(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    raw = _raw(run, raw_price="Sob consulta", source_url="https://fixture.local/no-rent")

    listing = normalize_raw_listing_to_listing(raw)

    assert listing.aluguel is None
    assert listing.confidence_status == ConfidenceStatus.INCOMPLETE


def test_probable_duplicate_marks_second_listing(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    first = _raw(run, source_url="https://fixture.local/duplicate")
    second = _raw(run, source_url="https://fixture.local/duplicate")

    first_listing = normalize_raw_listing_to_listing(first)
    second_listing = normalize_raw_listing_to_listing(second)

    assert first_listing.confidence_status == ConfidenceStatus.RELIABLE
    assert second_listing.confidence_status == ConfidenceStatus.PROBABLE_DUPLICATE


def test_normalize_search_run_processes_all_raw_and_recalculates_totals(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    _raw(run, source_url="https://fixture.local/one")
    _raw(run, raw_area="", source_url="https://fixture.local/two")
    _raw(run, raw_price="", source_url="https://fixture.local/three")

    summary = normalize_search_run(run)
    run.refresh_from_db()

    assert summary["raw_processed"] == 3
    assert summary["listings_created"] == 3
    assert RawListing.objects.filter(search_run=run).count() == 3
    assert Listing.objects.filter(raw_listing__search_run=run).count() == 3
    assert run.total_raw_collected == 3
    assert run.total_normalized == 3
    assert market_summary()["total_raw_without_listing"] == 0
    assert Listing.objects.filter(raw_listing__search_run=run, is_opportunity=True).count() == 0


def test_normalize_pending_raw_listings_respects_limit(db):
    run = SearchRun.objects.create(source_name="normalization", bairro="Asa Sul")
    _raw(run, source_url="https://fixture.local/one")
    _raw(run, source_url="https://fixture.local/two")

    summary = normalize_pending_raw_listings(limit=1)

    assert summary["raw_processed"] == 1
    assert Listing.objects.count() == 1


def test_normalization_gate_passes_and_negative_validator_fails(db):
    result = run_normalization_gate()

    assert result.passed, result.message

    negative = _validate_normalization_state(
        raw_before=1,
        raw_after=1,
        total_raw_collected=1,
        total_normalized=1,
        raw_without_listing=0,
        listings=Listing.objects.none(),
    )
    assert not negative.passed


def test_normalize_pending_script_prints_summary(db, capsys):
    run = SearchRun.objects.create(source_name="normalization-script", bairro="Asa Sul")
    _raw(run, source_url="https://fixture.local/script")

    exit_code = normalize_pending_script_main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "RawListings processados: 1" in output
    assert "Listings criados: 1" in output
