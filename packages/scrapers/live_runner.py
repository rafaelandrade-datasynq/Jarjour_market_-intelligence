from dataclasses import dataclass

from market.models import Listing, RawListing
from market.services.totals import recalculate_search_run_totals

from packages.scrapers.dfimoveis_live import (
    LivePreflightResult,
    LiveScrapingDisabledError,
    run_dfimoveis_live_preflight,
)
from packages.scrapers.live_config import (
    LIVE_MIN_CANDIDATES_FOR_COMPLETE,
    LiveScrapingConfig,
)
from packages.scrapers.persistence import persist_scraper_result


@dataclass(frozen=True)
class LiveRunnerResult:
    mode: str
    target_url: str
    candidates_extracted: int
    raw_listings_persisted: int
    listings_created: int
    evidence_path: str
    blocked: bool
    insufficient_result: bool
    message: str
    search_run_id: int | None = None


def run_live_preflight(
    *,
    query: dict[str, str],
    config: LiveScrapingConfig,
    evidence_root,
    source_name: str = "dfimoveis",
    preflight_func=run_dfimoveis_live_preflight,
) -> LiveRunnerResult:
    if not config.enabled:
        raise LiveScrapingDisabledError(
            "Live scraping disabled. Set ENABLE_LIVE_SCRAPING=true to run preflight."
        )
    preflight: LivePreflightResult = preflight_func(
        query=query,
        config=config,
        evidence_root=evidence_root,
    )
    scrape_result = preflight.scrape_result
    insufficient = scrape_result.raw_count < LIVE_MIN_CANDIDATES_FOR_COMPLETE
    if config.dry_run:
        return _result(
            mode="dry-run",
            preflight=preflight,
            raw_persisted=0,
            listings_created=0,
            insufficient=insufficient,
            message="Dry-run completed; no RawListing persisted.",
        )

    before_listing_count = Listing.objects.count()
    run = persist_scraper_result(
        scrape_result,
        source_name=source_name,
        bairro=query.get("bairro", ""),
        tipo_imovel=query.get("tipo", ""),
        finalidade=query.get("finalidade", ""),
    )
    if insufficient:
        run.status = "INCOMPLETE"
        run.save(update_fields=["status", "updated_at"])
        recalculate_search_run_totals(run)

    raw_persisted = RawListing.objects.filter(search_run=run).count()
    listings_created = Listing.objects.count() - before_listing_count
    return _result(
        mode="persistent",
        preflight=preflight,
        raw_persisted=raw_persisted,
        listings_created=listings_created,
        insufficient=insufficient,
        message="Live preflight persisted RawListing only.",
        search_run_id=run.id,
    )


def _result(
    *,
    mode: str,
    preflight: LivePreflightResult,
    raw_persisted: int,
    listings_created: int,
    insufficient: bool,
    message: str,
    search_run_id: int | None = None,
) -> LiveRunnerResult:
    return LiveRunnerResult(
        mode=mode,
        target_url=preflight.target_url,
        candidates_extracted=preflight.scrape_result.raw_count,
        raw_listings_persisted=raw_persisted,
        listings_created=listings_created,
        evidence_path=preflight.evidence_path,
        blocked=preflight.blocked,
        insufficient_result=insufficient,
        message=message,
        search_run_id=search_run_id,
    )
