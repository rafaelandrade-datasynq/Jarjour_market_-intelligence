import os
from dataclasses import dataclass

DEFAULT_MAX_PAGES = 1
DEFAULT_MAX_CANDIDATES = 20
DEFAULT_TIMEOUT_SECONDS = 30
LIVE_MIN_CANDIDATES_FOR_COMPLETE = 20


@dataclass(frozen=True)
class LiveScrapingConfig:
    enabled: bool = False
    dry_run: bool = True
    max_pages: int = DEFAULT_MAX_PAGES
    max_candidates: int = DEFAULT_MAX_CANDIDATES
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


def load_live_scraping_config(environ: dict[str, str] | None = None) -> LiveScrapingConfig:
    env = environ if environ is not None else os.environ
    return LiveScrapingConfig(
        enabled=_parse_bool(env.get("ENABLE_LIVE_SCRAPING"), default=False),
        dry_run=_parse_bool(env.get("LIVE_SCRAPING_DRY_RUN"), default=True),
        max_pages=_parse_int(
            env.get("LIVE_SCRAPING_MAX_PAGES"),
            default=DEFAULT_MAX_PAGES,
            minimum=1,
            maximum=DEFAULT_MAX_PAGES,
        ),
        max_candidates=_parse_int(
            env.get("LIVE_SCRAPING_MAX_CANDIDATES"),
            default=DEFAULT_MAX_CANDIDATES,
            minimum=1,
            maximum=DEFAULT_MAX_CANDIDATES,
        ),
        timeout_seconds=_parse_int(
            env.get("LIVE_SCRAPING_TIMEOUT_SECONDS"),
            default=DEFAULT_TIMEOUT_SECONDS,
            minimum=1,
            maximum=DEFAULT_TIMEOUT_SECONDS,
        ),
    )


def _parse_bool(value: str | None, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return default


def _parse_int(value: str | None, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default
    if parsed < minimum:
        return default
    return min(parsed, maximum)
