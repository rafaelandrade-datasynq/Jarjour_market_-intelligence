from decimal import Decimal

from market.models import ConfidenceStatus, Listing, RawListing, SearchRun


def test_models_exist_and_compute_rent_per_m2(db):
    run = SearchRun.objects.create(source_name="unit")
    raw = RawListing.objects.create(search_run=run, source_name="unit", raw_title="Sala teste")
    listing = Listing.objects.create(
        raw_listing=raw,
        source_name="unit",
        endereco="SCS Quadra 1",
        bairro="Asa Sul",
        tipo_imovel="Sala",
        finalidade="Aluguel",
        area_m2=Decimal("50"),
        aluguel=Decimal("5000"),
        confidence_status=ConfidenceStatus.RELIABLE,
    )
    assert listing.aluguel_m2 == Decimal("100")
    assert listing.raw_listing == raw
