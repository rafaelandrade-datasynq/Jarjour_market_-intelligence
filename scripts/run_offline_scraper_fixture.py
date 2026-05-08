import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "apps" / "server"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SERVER))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from market.models import Listing, RawListing  # noqa: E402

from packages.scrapers.dfimoveis import DFImoveisOfflineScraper  # noqa: E402
from packages.scrapers.evidence import save_offline_fixture_evidence  # noqa: E402
from packages.scrapers.persistence import persist_scraper_result  # noqa: E402


def main() -> int:
    fixture_path = (
        ROOT
        / "packages"
        / "scrapers"
        / "fixtures"
        / "dfimoveis_search_results_sample.html"
    )
    html = fixture_path.read_text(encoding="utf-8")
    initial_result = DFImoveisOfflineScraper().collect_from_html(html)
    evidence_path = save_offline_fixture_evidence(
        html,
        evidence_root=settings.REPO_ROOT / "data" / "evidence",
        source_name="dfimoveis",
        fixture_name=fixture_path.name,
        candidate_count=initial_result.raw_count,
    )
    result = DFImoveisOfflineScraper().collect_from_html(
        html,
        evidence_path=str(evidence_path.relative_to(ROOT)),
    )
    before_listing_count = Listing.objects.count()
    run = persist_scraper_result(
        result,
        bairro="Brasília",
        tipo_imovel="Comercial",
        finalidade="Aluguel",
    )
    raw_created = RawListing.objects.filter(search_run=run).count()
    listings_created = Listing.objects.count() - before_listing_count
    raw_without_listing = RawListing.objects.filter(search_run=run, listing__isnull=True).count()
    print(f"Fixture: {fixture_path.relative_to(ROOT)}")
    print(f"Candidates extracted: {result.raw_count}")
    print(f"RawListings created: {raw_created}")
    print(f"Listings created: {listings_created}")
    print(f"total_raw_collected: {run.total_raw_collected}")
    print(f"total_normalized: {run.total_normalized}")
    print(f"total_raw_without_listing: {raw_without_listing}")
    print(f"Evidence: {evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
