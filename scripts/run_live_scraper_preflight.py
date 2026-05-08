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

from packages.scrapers.dfimoveis_live import LiveScrapingDisabledError  # noqa: E402
from packages.scrapers.live_config import load_live_scraping_config  # noqa: E402
from packages.scrapers.live_runner import run_live_preflight  # noqa: E402


def main() -> int:
    config = load_live_scraping_config()
    if not config.enabled:
        print("Live scraping disabled. Set ENABLE_LIVE_SCRAPING=true to run preflight.")
        return 2

    query = {
        "bairro": os.environ.get("LIVE_SCRAPING_BAIRRO", "Asa Sul"),
        "tipo": os.environ.get("LIVE_SCRAPING_TIPO", "Apartamento"),
        "finalidade": os.environ.get("LIVE_SCRAPING_FINALIDADE", "aluguel"),
    }
    try:
        result = run_live_preflight(
            query=query,
            config=config,
            evidence_root=settings.REPO_ROOT / "data" / "evidence",
        )
    except LiveScrapingDisabledError as exc:
        print(str(exc))
        return 2

    print(f"Modo: {result.mode}")
    print(f"URL consultada: {result.target_url}")
    print(f"Candidatos extraidos: {result.candidates_extracted}")
    print(f"RawListings persistidos: {result.raw_listings_persisted}")
    print(f"Listings criados: {result.listings_created}")
    print(f"Evidencia: {result.evidence_path}")
    print(f"Bloqueio detectado: {result.blocked}")
    print(f"Resultado insuficiente: {result.insufficient_result}")
    print(result.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
