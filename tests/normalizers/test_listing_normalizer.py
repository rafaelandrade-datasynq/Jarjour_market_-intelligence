from decimal import Decimal

from market.models import ConfidenceStatus, RawListing, ReviewStatus, SearchRun

from packages.normalizers.listing_normalizer import normalize_raw_listing


def test_listing_normalizer_builds_reliable_data(db):
    run = SearchRun.objects.create(source_name="test", bairro="Asa Sul", finalidade="Aluguel")
    raw = RawListing.objects.create(
        search_run=run,
        source_name="test",
        source_url="https://fixture.local/listing",
        raw_title="Sala comercial para aluguel",
        raw_description="Com copa.",
        raw_address="CLS 308 Bloco B",
        raw_price="R$ 3.500,00",
        raw_area="45 m²",
        raw_condominium="R$ 500",
        raw_contact="Equipe",
        raw_phone="(61) 3000-0000",
    )

    data = normalize_raw_listing(raw)

    assert data.aluguel == Decimal("3500.00")
    assert data.area_m2 == Decimal("45")
    assert data.aluguel_m2 == Decimal("77.78")
    assert data.condominio_m2 == Decimal("11.11")
    assert data.confidence_status == ConfidenceStatus.RELIABLE
    assert data.review_status == ReviewStatus.NOT_REVIEWED
    assert data.is_opportunity is False
