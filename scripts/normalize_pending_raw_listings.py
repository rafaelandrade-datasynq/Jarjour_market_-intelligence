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

from market.services.normalization import normalize_pending_raw_listings  # noqa: E402


def main() -> int:
    summary = normalize_pending_raw_listings()
    print(f"RawListings processados: {summary['raw_processed']}")
    print(f"Listings criados: {summary['listings_created']}")
    print(f"Listings atualizados: {summary['listings_updated']}")
    print(f"Confiaveis: {summary['reliable']}")
    print(f"Para revisar: {summary['review']}")
    print(f"Incompletos: {summary['incomplete']}")
    print(f"Duplicados provaveis: {summary['probable_duplicates']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
