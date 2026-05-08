from pathlib import Path

from packages.scrapers.dfimoveis import DFImoveisOfflineScraper

FIXTURE = Path("packages/scrapers/fixtures/dfimoveis_search_results_sample.html")


def test_official_dfimoveis_fixture_exists_and_has_minimum_candidates():
    assert FIXTURE.exists()
    html = FIXTURE.read_text(encoding="utf-8")

    assert html.count('data-listing="dfimoveis"') >= 8


def test_dfimoveis_parser_reads_official_offline_fixture():
    html = FIXTURE.read_text(encoding="utf-8")
    result = DFImoveisOfflineScraper().collect_from_html(html, evidence_path="tests/fixture.html")

    assert result.source_name == "dfimoveis"
    assert result.raw_count >= 8
    assert result.listings[0].title == "Sala comercial para aluguel na Asa Sul"
    assert result.listings[0].address == "CLS 308 Bloco B, Asa Sul, Brasília"
    assert result.listings[0].price == "R$ 8.900"
    assert (
        result.listings[0].source_url
        == "https://fixture.local/dfimoveis/sala-comercial-asa-sul-completa"
    )
    assert result.listings[0].payload["offline_fixture"] is True


def test_dfimoveis_parser_preserves_representative_incomplete_candidates():
    html = FIXTURE.read_text(encoding="utf-8")
    result = DFImoveisOfflineScraper().collect_from_html(html, evidence_path="tests/fixture.html")
    listings = result.listings

    assert any(not listing.condominium for listing in listings)
    assert any(not listing.area for listing in listings)
    assert any(not listing.phone for listing in listings)
    assert any(listing.price == "R$ 32.450,75" for listing in listings)
    assert any(listing.address == "Asa Norte" for listing in listings)
    assert any(listing.source_url for listing in listings)

    addresses = [listing.address for listing in listings if listing.address]
    assert len(addresses) > len(set(addresses))
