from pathlib import Path

from packages.quality_gates.scraper_offline_gate import run_scraper_offline_gate
from packages.scrapers.contracts import ScrapedListing, ScraperResult


def test_scraper_offline_gate_validates_fixture_contract(db):
    result = run_scraper_offline_gate(Path.cwd())

    assert result.passed, result.message


def test_scraper_offline_gate_fails_when_parser_returns_less_than_8(db, monkeypatch):
    listings = [
        ScrapedListing(
            source_name="dfimoveis",
            title=f"Fixture {index}",
            address=f"Endereço {index}",
            source_url=f"https://fixture.local/{index}",
        )
        for index in range(7)
    ]

    def fake_collect_from_html(self, html: str, evidence_path: str = "") -> ScraperResult:
        return ScraperResult(
            source_name="dfimoveis",
            listings=listings,
            evidence_path=evidence_path,
        )

    monkeypatch.setattr(
        "packages.scrapers.dfimoveis.DFImoveisOfflineScraper.collect_from_html",
        fake_collect_from_html,
    )

    result = run_scraper_offline_gate(Path.cwd())

    assert not result.passed
    assert "fewer than 8" in result.message


def test_scraper_tests_use_official_fixture_only():
    duplicate_fixture = Path("tests/fixtures/dfimoveis_search_results_sample.html")

    assert not duplicate_fixture.exists()


def test_offline_scraper_script_uses_official_fixture():
    script = Path("scripts/run_offline_scraper_fixture.py").read_text(encoding="utf-8")

    assert '"packages"' in script
    assert '"scrapers"' in script
    assert '"fixtures"' in script
    assert '"dfimoveis_search_results_sample.html"' in script
