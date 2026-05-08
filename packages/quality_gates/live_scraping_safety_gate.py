from dataclasses import dataclass
from pathlib import Path

from packages.scrapers.live_config import load_live_scraping_config


@dataclass(frozen=True)
class LiveScrapingSafetyResult:
    passed: bool
    message: str


def run_live_scraping_safety_gate(root: Path) -> LiveScrapingSafetyResult:
    config = load_live_scraping_config(environ={})
    if config.enabled:
        return LiveScrapingSafetyResult(False, "Live scraping must be disabled by default.")
    if not config.dry_run:
        return LiveScrapingSafetyResult(False, "Live scraping dry-run must be true by default.")
    if config.max_pages > 1:
        return LiveScrapingSafetyResult(False, "Live scraping max_pages default must be <= 1.")
    if config.max_candidates > 20:
        return LiveScrapingSafetyResult(
            False,
            "Live scraping max_candidates default must be <= 20.",
        )

    scan_files = [
        *list((root / "packages" / "scrapers").glob("*.py")),
        root / "scripts" / "run_live_scraper_preflight.py",
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in scan_files if path.exists())
    forbidden = [
        "proxy=",
        "captcha_solver",
        "captcha bypass",
        "bypass captcha",
        "user_agent=",
        "rotate_user",
        "login(",
        "normalize_search_run(",
        "normalize_pending_raw_listings(",
        "\nListing.objects.create",
    ]
    for pattern in forbidden:
        if pattern in contents:
            return LiveScrapingSafetyResult(
                False,
                f"Live scraping safety gate found forbidden pattern: {pattern}",
            )

    script = root / "scripts" / "run_live_scraper_preflight.py"
    script_text = script.read_text(encoding="utf-8")
    if "if not config.enabled" not in script_text:
        return LiveScrapingSafetyResult(
            False,
            "Live preflight script does not enforce feature flag.",
        )

    test_contents = "\n".join(
        path.read_text(encoding="utf-8") for path in (root / "tests" / "scrapers").glob("*.py")
    )
    forbidden_tests = ["sync_playwright(", ".goto(", "chromium.launch", "requests.", "httpx."]
    for pattern in forbidden_tests:
        if pattern in test_contents:
            return LiveScrapingSafetyResult(
                False,
                f"Scraper tests contain forbidden live access pattern: {pattern}",
            )

    return LiveScrapingSafetyResult(True, "Live scraping preflight is guarded by safe defaults.")
