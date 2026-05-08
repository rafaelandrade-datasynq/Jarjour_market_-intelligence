from django.db import transaction
from django.utils import timezone
from market.models import RawListing, SearchRun
from market.services.totals import recalculate_search_run_totals

from packages.scrapers.contracts import ScraperResult


@transaction.atomic
def persist_scraper_result(
    result: ScraperResult,
    *,
    source_name: str | None = None,
    bairro: str = "",
    tipo_imovel: str = "",
    finalidade: str = "",
) -> SearchRun:
    run = SearchRun.objects.create(
        source_name=source_name or result.source_name,
        bairro=bairro,
        tipo_imovel=tipo_imovel,
        finalidade=finalidade,
        status="COMPLETED",
        finished_at=timezone.now(),
    )

    for listing in result.listings:
        RawListing.objects.create(
            search_run=run,
            source_name=listing.source_name,
            source_url=listing.source_url,
            raw_title=listing.title,
            raw_description=listing.description,
            raw_address=listing.address,
            raw_price=listing.price,
            raw_area=listing.area,
            raw_condominium=listing.condominium,
            raw_contact=listing.contact,
            raw_phone=listing.phone,
            raw_payload_json={
                **listing.payload,
                "evidence_path": result.evidence_path,
                "offline_first": True,
            },
        )

    return recalculate_search_run_totals(run)
