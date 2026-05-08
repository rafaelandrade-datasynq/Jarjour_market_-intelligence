from packages.scrapers.live_config import load_live_scraping_config


def test_live_config_defaults_are_safe():
    config = load_live_scraping_config(environ={})

    assert config.enabled is False
    assert config.dry_run is True
    assert config.max_pages == 1
    assert config.max_candidates == 20
    assert config.timeout_seconds == 30


def test_live_config_invalid_values_fall_back_or_clamp_to_safe_defaults():
    config = load_live_scraping_config(
        environ={
            "ENABLE_LIVE_SCRAPING": "false",
            "LIVE_SCRAPING_DRY_RUN": "not-bool",
            "LIVE_SCRAPING_MAX_PAGES": "5",
            "LIVE_SCRAPING_MAX_CANDIDATES": "200",
            "LIVE_SCRAPING_TIMEOUT_SECONDS": "abc",
        }
    )

    assert config.enabled is False
    assert config.dry_run is True
    assert config.max_pages == 1
    assert config.max_candidates == 20
    assert config.timeout_seconds == 30
