from pathlib import Path

from packages.quality_gates.live_scraping_safety_gate import run_live_scraping_safety_gate


def test_live_scraping_safety_gate_passes_with_safe_defaults():
    result = run_live_scraping_safety_gate(Path.cwd())

    assert result.passed, result.message


def test_live_scraping_safety_gate_fails_if_default_enabled(monkeypatch):
    from packages.quality_gates import live_scraping_safety_gate
    from packages.scrapers.live_config import LiveScrapingConfig

    monkeypatch.setattr(
        live_scraping_safety_gate,
        "load_live_scraping_config",
        lambda environ=None: LiveScrapingConfig(enabled=True),
    )

    result = live_scraping_safety_gate.run_live_scraping_safety_gate(Path.cwd())

    assert not result.passed
    assert "disabled by default" in result.message


def test_live_scraping_safety_gate_fails_if_default_dry_run_is_false(monkeypatch):
    from packages.quality_gates import live_scraping_safety_gate
    from packages.scrapers.live_config import LiveScrapingConfig

    monkeypatch.setattr(
        live_scraping_safety_gate,
        "load_live_scraping_config",
        lambda environ=None: LiveScrapingConfig(enabled=False, dry_run=False),
    )

    result = live_scraping_safety_gate.run_live_scraping_safety_gate(Path.cwd())

    assert not result.passed
    assert "dry-run" in result.message


def test_live_scraping_safety_gate_fails_if_default_max_pages_is_too_high(monkeypatch):
    from packages.quality_gates import live_scraping_safety_gate
    from packages.scrapers.live_config import LiveScrapingConfig

    monkeypatch.setattr(
        live_scraping_safety_gate,
        "load_live_scraping_config",
        lambda environ=None: LiveScrapingConfig(enabled=False, max_pages=2),
    )

    result = live_scraping_safety_gate.run_live_scraping_safety_gate(Path.cwd())

    assert not result.passed
    assert "max_pages" in result.message


def test_live_scraping_safety_gate_fails_on_forbidden_bypass_pattern():
    marker = Path("packages/scrapers/_temporary_forbidden_live_test.py")
    marker.write_text("proxy='http://fixture.local'\n", encoding="utf-8")
    try:
        result = run_live_scraping_safety_gate(Path.cwd())
    finally:
        marker.unlink(missing_ok=True)

    assert not result.passed
    assert "proxy=" in result.message
