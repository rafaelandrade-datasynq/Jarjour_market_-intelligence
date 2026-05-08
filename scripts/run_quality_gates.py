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

from packages.quality_gates.data_visibility_gate import run_data_visibility_gate  # noqa: E402
from packages.quality_gates.excel_contract_gate import run_excel_contract_gate  # noqa: E402
from packages.quality_gates.hallucination_gate import run_hallucination_gate  # noqa: E402
from packages.quality_gates.live_scraping_safety_gate import (  # noqa: E402
    run_live_scraping_safety_gate,
)
from packages.quality_gates.normalization_gate import run_normalization_gate  # noqa: E402
from packages.quality_gates.review_flow_gate import run_review_flow_gate  # noqa: E402
from packages.quality_gates.scraper_offline_gate import run_scraper_offline_gate  # noqa: E402


def main() -> int:
    checks = [
        run_data_visibility_gate(),
        run_excel_contract_gate(),
        run_review_flow_gate(),
        run_scraper_offline_gate(ROOT),
        run_normalization_gate(),
        run_live_scraping_safety_gate(ROOT),
        run_hallucination_gate(ROOT),
    ]
    failed = False
    for check in checks:
        if isinstance(check, tuple):
            passed, message = check
        else:
            passed, message = check.passed, check.message
        print(f"{'PASS' if passed else 'FAIL'} - {message}")
        failed = failed or not passed
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
