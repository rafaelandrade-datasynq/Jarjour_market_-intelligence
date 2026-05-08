from dataclasses import dataclass
from urllib.parse import urlencode

from packages.scrapers.contracts import ScraperResult
from packages.scrapers.dfimoveis import DFImoveisOfflineScraper
from packages.scrapers.evidence import save_live_preflight_evidence
from packages.scrapers.live_config import LiveScrapingConfig


class LiveScrapingDisabledError(RuntimeError):
    pass


@dataclass(frozen=True)
class LivePreflightResult:
    scrape_result: ScraperResult
    target_url: str
    evidence_path: str
    blocked: bool = False
    message: str = ""


def build_dfimoveis_preflight_url(query: dict[str, str]) -> str:
    safe_query = {
        "bairro": query.get("bairro", "Asa Sul"),
        "tipo": query.get("tipo", "Apartamento"),
        "finalidade": query.get("finalidade", "aluguel"),
    }
    return "https://www.dfimoveis.com.br/busca?" + urlencode(safe_query)


def run_dfimoveis_live_preflight(
    *,
    query: dict[str, str],
    config: LiveScrapingConfig,
    evidence_root,
) -> LivePreflightResult:
    if not config.enabled:
        raise LiveScrapingDisabledError(
            "Live scraping disabled. Set ENABLE_LIVE_SCRAPING=true to run preflight."
        )

    target_url = build_dfimoveis_preflight_url(query)
    html, screenshot_bytes, blocked, message = _capture_with_playwright(target_url, config)
    parser = DFImoveisOfflineScraper()
    parsed = parser.collect_from_html(html)
    limited_listings = parsed.listings[: config.max_candidates]
    evidence_path = save_live_preflight_evidence(
        html,
        evidence_root=evidence_root,
        source_name="dfimoveis",
        target_url=target_url,
        candidate_count=len(limited_listings),
        status="BLOCKED" if blocked else "INCOMPLETE",
        blocked=blocked,
        screenshot_bytes=screenshot_bytes,
    )
    result = ScraperResult(
        source_name="dfimoveis",
        listings=limited_listings,
        evidence_path=str(evidence_path),
    )
    return LivePreflightResult(
        scrape_result=result,
        target_url=target_url,
        evidence_path=str(evidence_path),
        blocked=blocked,
        message=message,
    )


def _capture_with_playwright(
    target_url: str,
    config: LiveScrapingConfig,
) -> tuple[str, bytes | None, bool, str]:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    timeout_ms = config.timeout_seconds * 1000
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
            html = page.content()
            screenshot = page.screenshot(full_page=True)
            browser.close()
    except PlaywrightTimeoutError:
        return "", None, True, "Timeout during controlled live preflight."

    lowered = html.lower()
    blocked = any(marker in lowered for marker in ["captcha", "login", "acesso negado"])
    message = "Blocked or login/CAPTCHA detected." if blocked else "Live preflight captured."
    return html, screenshot, blocked, message
