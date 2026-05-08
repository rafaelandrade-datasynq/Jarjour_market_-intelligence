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

from exports.services import save_carol_workbook  # noqa: E402

if __name__ == "__main__":
    path = save_carol_workbook()
    print(path)
