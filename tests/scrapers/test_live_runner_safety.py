from pathlib import Path

import pytest
from market.models import Listing, RawListing

from packages.scrapers.contracts import ScrapedListing, ScraperResult
from packages.scrapers.dfimoveis_live import (
    LivePreflightResult,
    LiveScrapingDisabledError,
    build_dfimoveis_preflight_url,
)
from packages.scrapers.live_config import LiveScrapingConfig
from packages.scrapers.live_runner import run_live_preflight

EVIDENCE_ROOT = Path("data/evidence/test-live")


def _fake_preflight(*, query, config, evidence_root):
    listings = [
        ScrapedListing(
            source_name="dfimoveis",
            title="Preflight fixture",
            address="Asa Sul",
            price="R$ 3.500",
            area="45 m²",
            source_url="https://fixture.local/live-preflight",
        )
    ]
    return LivePreflightResult(
        scrape_result=ScraperResult(
            source_name="dfimoveis",
            listings=listings,
            evidence_path=str(Path(evidence_root) / "fixture"),
        ),
        target_url=build_dfimoveis_preflight_url(query),
        evidence_path=str(Path(evidence_root) / "fixture"),
        blocked=False,
        message="simulated",
    )


def test_live_runner_aborts_when_disabled_before_capture(db):
    called = False

    def should_not_be_called(*, query, config, evidence_root):
        nonlocal called
        called = True
        return _fake_preflight(query=query, config=config, evidence_root=evidence_root)

    with pytest.raises(LiveScrapingDisabledError):
        run_live_preflight(
            query={"bairro": "Asa Sul"},
            config=LiveScrapingConfig(enabled=False),
            evidence_root=EVIDENCE_ROOT,
            preflight_func=should_not_be_called,
        )

    assert called is False


def test_live_runner_dry_run_does_not_persist(db):
    result = run_live_preflight(
        query={"bairro": "Asa Sul", "tipo": "Apartamento", "finalidade": "aluguel"},
        config=LiveScrapingConfig(enabled=True, dry_run=True),
        evidence_root=EVIDENCE_ROOT,
        preflight_func=_fake_preflight,
    )

    assert result.mode == "dry-run"
    assert result.candidates_extracted == 1
    assert result.raw_listings_persisted == 0
    assert RawListing.objects.count() == 0
    assert Listing.objects.count() == 0


def test_live_runner_persistent_mode_creates_raw_only(db):
    result = run_live_preflight(
        query={"bairro": "Asa Sul", "tipo": "Apartamento", "finalidade": "aluguel"},
        config=LiveScrapingConfig(enabled=True, dry_run=False),
        evidence_root=EVIDENCE_ROOT,
        preflight_func=_fake_preflight,
    )

    assert result.mode == "persistent"
    assert result.raw_listings_persisted == 1
    assert result.listings_created == 0
    assert RawListing.objects.count() == 1
    assert Listing.objects.count() == 0


def test_live_preflight_url_uses_safe_query_defaults():
    url = build_dfimoveis_preflight_url({})

    assert "bairro=Asa+Sul" in url
    assert "tipo=Apartamento" in url
    assert "finalidade=aluguel" in url
