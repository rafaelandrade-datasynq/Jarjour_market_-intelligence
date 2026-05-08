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

from market.services.demo_data import create_demo_search_run  # noqa: E402

if __name__ == "__main__":
    run = create_demo_search_run()
    print(f"Created demo SearchRun {run.id} with {run.total_raw_collected} raw listings.")
