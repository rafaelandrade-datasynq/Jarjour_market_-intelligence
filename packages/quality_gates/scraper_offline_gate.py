from dataclasses import dataclass
from pathlib import Path

from django.db import transaction
from market.models import Listing, RawListing

from packages.scrapers.contracts import ScrapedListing, ScraperResult
from packages.scrapers.dfimoveis import DFImoveisOfflineScraper
from packages.scrapers.persistence import persist_scraper_result

MIN_OFFLINE_CANDIDATES = 8


@dataclass(frozen=True)
class ScraperOfflineResult:
    passed: bool
    message: str


def run_scraper_offline_gate(root: Path) -> ScraperOfflineResult:
    fixture_path = (
        root
        / "packages"
        / "scrapers"
        / "fixtures"
        / "dfimoveis_search_results_sample.html"
    )
    if not fixture_path.exists():
        return ScraperOfflineResult(False, "DF Imóveis offline fixture is missing.")

    html = fixture_path.read_text(encoding="utf-8")
    recognized_count = html.count('data-listing="dfimoveis"')
    if recognized_count < MIN_OFFLINE_CANDIDATES:
        return ScraperOfflineResult(
            False,
            "DF Imóveis offline fixture has fewer than 8 recognizable listings.",
        )

    result = DFImoveisOfflineScraper().collect_from_html(html, evidence_path="gate")
    if result.source_name != "dfimoveis":
        return ScraperOfflineResult(False, "DF Imóveis scraper returned wrong source.")
    if result.raw_count < MIN_OFFLINE_CANDIDATES:
        return ScraperOfflineResult(
            False,
            "DF Imóveis offline parser returned fewer than 8 candidates.",
        )
    if any(not listing.title or not listing.source_url for listing in result.listings):
        return ScraperOfflineResult(False, "DF Imóveis offline parser returned incomplete rows.")
    coverage_error = _validate_fixture_coverage(result)
    if coverage_error:
        return ScraperOfflineResult(False, coverage_error)

    persistence_error = _validate_raw_persistence(result)
    if persistence_error:
        return ScraperOfflineResult(False, persistence_error)

    forbidden = [
        "requests.",
        "httpx.",
        "urllib.request",
        "aiohttp",
        "sync_playwright(",
        "async_playwright(",
        "chromium.launch",
        "firefox.launch",
        "webkit.launch",
        ".goto(",
    ]
    scan_files = [
        *[
            path
            for path in (root / "packages" / "scrapers").glob("*.py")
            if path.name not in {"dfimoveis_live.py", "live_runner.py"}
        ],
        root / "scripts" / "run_offline_scraper_fixture.py",
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in scan_files if path.exists())
    if any(pattern in contents for pattern in forbidden):
        return ScraperOfflineResult(False, "Offline scraper gate found live access code.")

    return ScraperOfflineResult(True, "Offline scraper fixture parses without live portal access.")


def _validate_fixture_coverage(result: ScraperResult) -> str:
    listings: list[ScrapedListing] = result.listings
    if not any(not listing.condominium for listing in listings):
        return "DF Imóveis fixture lacks a candidate without condominium."
    if not any(not listing.area for listing in listings):
        return "DF Imóveis fixture lacks a candidate without area."
    if not any(not listing.phone for listing in listings):
        return "DF Imóveis fixture lacks a candidate without phone."
    if not any(listing.address == "Asa Norte" for listing in listings):
        return "DF Imóveis fixture lacks a partial-address candidate."
    addresses = [listing.address for listing in listings if listing.address]
    if len(addresses) == len(set(addresses)):
        return "DF Imóveis fixture lacks a probable duplicate candidate."
    return ""


def _validate_raw_persistence(result: ScraperResult) -> str:
    with transaction.atomic():
        before_listing_count = Listing.objects.count()
        run = persist_scraper_result(
            result,
            bairro="Gate",
            tipo_imovel="Comercial",
            finalidade="Aluguel",
        )
        raw_created = RawListing.objects.filter(search_run=run).count()
        listing_delta = Listing.objects.count() - before_listing_count
        raw_without_listing = RawListing.objects.filter(
            search_run=run,
            listing__isnull=True,
        ).count()
        transaction.set_rollback(True)

        if raw_created != result.raw_count:
            return "Offline scraper persistence did not create one RawListing per candidate."
        if listing_delta != 0:
            return "Offline scraper persistence created Listing rows."
        if run.total_raw_collected != result.raw_count:
            return "Offline scraper SearchRun total_raw_collected is incorrect."
        if run.total_normalized != 0:
            return "Offline scraper SearchRun total_normalized must remain zero."
        if raw_without_listing != result.raw_count:
            return "Offline scraper hid RawListing rows without Listing."
    return ""
