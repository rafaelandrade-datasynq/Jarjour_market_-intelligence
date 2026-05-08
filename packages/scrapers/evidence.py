import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.utils import timezone


@dataclass(frozen=True)
class EvidencePointer:
    raw_listing_id: int
    path: Path
    note: str = ""


def save_html_evidence(
    html: str,
    *,
    evidence_dir: Path,
    source_name: str,
    filename: str = "offline_fixture.html",
) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{source_name}-{filename}"
    path.write_text(html, encoding="utf-8")
    return path


def save_offline_fixture_evidence(
    html: str,
    *,
    evidence_root: Path,
    source_name: str,
    fixture_name: str,
    candidate_count: int,
) -> Path:
    collected_at = timezone.now()
    evidence_dir = (
        evidence_root
        / source_name
        / collected_at.strftime("%Y%m%d-%H%M%S-%f")
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)

    (evidence_dir / "page.html").write_text(html, encoding="utf-8")
    meta: dict[str, Any] = {
        "source_name": source_name,
        "fixture_name": fixture_name,
        "collected_at": collected_at.isoformat(),
        "candidate_count": candidate_count,
        "mode": "offline_fixture",
    }
    (evidence_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return evidence_dir


def save_live_preflight_evidence(
    html: str,
    *,
    evidence_root: Path,
    source_name: str,
    target_url: str,
    candidate_count: int,
    status: str,
    blocked: bool = False,
    screenshot_bytes: bytes | None = None,
) -> Path:
    collected_at = timezone.now()
    evidence_dir = evidence_root / source_name / collected_at.strftime("%Y%m%d-%H%M%S-%f")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "page.html").write_text(html, encoding="utf-8")
    if screenshot_bytes:
        (evidence_dir / "screenshot.png").write_bytes(screenshot_bytes)
    meta: dict[str, Any] = {
        "source_name": source_name,
        "target_url": target_url,
        "collected_at": collected_at.isoformat(),
        "candidate_count": candidate_count,
        "mode": "live_preflight",
        "status": status,
        "blocked": blocked,
    }
    (evidence_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return evidence_dir
