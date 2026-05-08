from market.models import ConfidenceStatus, Listing, RawListing, SearchRun
from market.selectors.summary import market_summary


def test_market_summary_counts_demo_statuses(demo_run):
    summary = market_summary()
    assert summary["total_raw_collected"] == 6
    assert summary["total_normalized"] == 6
    assert summary["total_raw_without_listing"] == 0
    assert summary["total_reliable"] == 2
    assert summary["total_review"] == 1
    assert summary["total_incomplete"] == 1
    assert summary["total_probable_duplicates"] == 1
    assert summary["total_discarded"] == 1
    assert summary["total_opportunities"] == 2
    assert summary["average_rent_m2"] is not None


def test_market_summary_counts_raw_without_listing(db):
    run = SearchRun.objects.create(source_name="unit")
    raw_with_listing = RawListing.objects.create(
        search_run=run,
        source_name="unit",
        raw_title="Sala normalizada",
    )
    RawListing.objects.create(search_run=run, source_name="unit", raw_title="Bruto pendente 1")
    RawListing.objects.create(search_run=run, source_name="unit", raw_title="Bruto pendente 2")
    Listing.objects.create(
        raw_listing=raw_with_listing,
        source_name="unit",
        endereco="SCN Quadra 1",
        bairro="Asa Norte",
        tipo_imovel="Sala",
        finalidade="Aluguel",
        confidence_status=ConfidenceStatus.RELIABLE,
    )

    summary = market_summary()

    assert summary["total_raw_collected"] == 3
    assert summary["total_normalized"] == 1
    assert summary["total_raw_without_listing"] == 2
