from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIR_NAMES = {".git", ".venv", "venv"}
EXCLUDED_FILE_NAMES = {".gitkeep", "README.md"}


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def is_within_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    return True


def is_excluded(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    return bool(parts & EXCLUDED_DIR_NAMES) or path.name in EXCLUDED_FILE_NAMES


def remove_path(path: Path, removed: list[str], failed: list[str]) -> None:
    if not path.exists() or not is_within_root(path) or is_excluded(path):
        return
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except PermissionError as exc:
        failed.append(f"{relative(path)} - PermissionError: {exc}")
    except OSError as exc:
        failed.append(f"{relative(path)} - {exc.__class__.__name__}: {exc}")
    else:
        removed.append(relative(path))


def iter_workspace(pattern: str):
    for path in ROOT.rglob(pattern):
        if is_excluded(path):
            continue
        yield path


def main() -> int:
    removed: list[str] = []
    failed: list[str] = []

    root_dirs = [
        ".ruff_cache",
        ".pytest_cache",
        ".mypy_cache",
        "jarjour_market_intelligence.egg-info",
        "htmlcov",
    ]
    for dirname in root_dirs:
        remove_path(ROOT / dirname, removed, failed)

    for path in list(ROOT.glob("*.egg-info")):
        remove_path(path, removed, failed)
    for path in list(ROOT.glob("pytest-cache-files-*")):
        remove_path(path, removed, failed)

    for path in list(iter_workspace("__pycache__")):
        remove_path(path, removed, failed)
    for path in list(iter_workspace("*.pyc")):
        remove_path(path, removed, failed)

    for path in list((ROOT / "data" / "exports").glob("*.xlsx")):
        remove_path(path, removed, failed)
    for path in list((ROOT / "data").rglob("*.log")):
        remove_path(path, removed, failed)

    remove_path(ROOT / ".coverage", removed, failed)

    print("Workspace cleanup complete.")
    print(f"Removed: {len(removed)}")
    for item in removed:
        print(f"  removed {item}")
    print(f"Failed: {len(failed)}")
    for item in failed:
        print(f"  warning {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
