import shutil
from pathlib import Path
from uuid import uuid4

from market.models import Listing, RawListing
from market.selectors.summary import market_summary

from packages.scrapers.dfimoveis import DFImoveisOfflineScraper
from packages.scrapers.evidence import save_offline_fixture_evidence
from packages.scrapers.persistence import persist_scraper_result

FIXTURE = Path("packages/scrapers/fixtures/dfimoveis_search_results_sample.html")


def test_scraper_persistence_creates_raw_listings_only(db):
    html = FIXTURE.read_text(encoding="utf-8")
    initial_result = DFImoveisOfflineScraper().collect_from_html(html)
    evidence_root = Path("data/evidence") / f"test-offline-{uuid4().hex}"
    evidence_path = save_offline_fixture_evidence(
        html,
        evidence_root=evidence_root,
        source_name="dfimoveis",
        fixture_name=FIXTURE.name,
        candidate_count=initial_result.raw_count,
    )
    result = DFImoveisOfflineScraper().collect_from_html(
        html,
        evidence_path=str(evidence_path),
    )

    run = persist_scraper_result(result, bairro="Brasília", finalidade="Aluguel")
    raw_queryset = RawListing.objects.filter(search_run=run).order_by("id")

    assert run.source_name == "dfimoveis"
    assert result.raw_count >= 8
    assert run.total_raw_collected == result.raw_count
    assert run.total_normalized == 0
    assert raw_queryset.count() == result.raw_count
    assert Listing.objects.count() == 0
    raw_without_listing = RawListing.objects.filter(search_run=run, listing__isnull=True).count()
    assert raw_without_listing == result.raw_count
    assert market_summary()["total_raw_without_listing"] == result.raw_count

    raw = raw_queryset.first()
    assert raw.raw_title == "Sala comercial para aluguel na Asa Sul"
    assert raw.raw_payload_json["offline_first"] is True
    assert raw.raw_payload_json["evidence_path"] == str(evidence_path)
    assert (evidence_path / "page.html").exists()
    assert (evidence_path / "meta.json").exists()

    shutil.rmtree(evidence_root, ignore_errors=True)
