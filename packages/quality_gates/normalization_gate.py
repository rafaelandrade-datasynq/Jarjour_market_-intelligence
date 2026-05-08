from dataclasses import dataclass

from django.db import transaction
from market.models import ConfidenceStatus, Listing, RawListing, SearchRun
from market.services.normalization import normalize_search_run


@dataclass(frozen=True)
class NormalizationGateResult:
    passed: bool
    message: str


def run_normalization_gate() -> NormalizationGateResult:
    with transaction.atomic():
        run = SearchRun.objects.create(
            source_name="normalization-gate",
            bairro="Asa Sul",
            tipo_imovel="Sala",
            finalidade="Aluguel",
        )
        RawListing.objects.create(
            search_run=run,
            source_name="normalization-gate",
            source_url="https://fixture.local/gate/complete",
            raw_title="Sala comercial para aluguel na Asa Sul",
            raw_address="CLS 308 Bloco B",
            raw_price="R$ 3.500,00",
            raw_area="45 m²",
            raw_condominium="R$ 500",
        )
        RawListing.objects.create(
            search_run=run,
            source_name="normalization-gate",
            source_url="https://fixture.local/gate/incomplete",
            raw_title="Sala sem aluguel",
            raw_address="Asa Sul",
            raw_price="Sob consulta",
            raw_area="40 m²",
        )
        raw_before = RawListing.objects.filter(search_run=run).count()

        normalize_search_run(run)
        run.refresh_from_db()
        listings = Listing.objects.filter(raw_listing__search_run=run)
        raw_after = RawListing.objects.filter(search_run=run).count()
        raw_without_listing = RawListing.objects.filter(
            search_run=run,
            listing__isnull=True,
        ).count()

        result = _validate_normalization_state(
            raw_before=raw_before,
            raw_after=raw_after,
            total_raw_collected=run.total_raw_collected,
            total_normalized=run.total_normalized,
            raw_without_listing=raw_without_listing,
            listings=listings,
        )
        transaction.set_rollback(True)
        return result


def _validate_normalization_state(
    *,
    raw_before: int,
    raw_after: int,
    total_raw_collected: int,
    total_normalized: int,
    raw_without_listing: int,
    listings,
) -> NormalizationGateResult:
    listing_count = listings.count()
    if raw_before == 0:
        return NormalizationGateResult(False, "Normalization gate requires RawListing rows.")
    if raw_after != raw_before:
        return NormalizationGateResult(False, "Normalization deleted RawListing rows.")
    if listing_count != raw_before:
        return NormalizationGateResult(
            False,
            "Normalization did not create Listing for each raw row.",
        )
    if listings.filter(is_opportunity=True).exists():
        return NormalizationGateResult(False, "Normalization marked opportunity automatically.")
    if not listings.filter(confidence_status=ConfidenceStatus.INCOMPLETE).exists():
        return NormalizationGateResult(
            False,
            "Incomplete raw data was not preserved as INCOMPLETE.",
        )
    if total_raw_collected != raw_before:
        return NormalizationGateResult(False, "SearchRun total_raw_collected changed incorrectly.")
    if total_normalized != listing_count:
        return NormalizationGateResult(False, "SearchRun total_normalized is incorrect.")
    if raw_without_listing != 0:
        return NormalizationGateResult(
            False,
            "RawListing without Listing remained after normalization.",
        )
    if listings.filter(confidence_status__in=["APPROVED", "REJECTED", "OPPORTUNITY"]).exists():
        return NormalizationGateResult(
            False,
            "confidence_status contains review status values.",
        )
    return NormalizationGateResult(True, "Normalization creates Listings without hiding raw data.")
