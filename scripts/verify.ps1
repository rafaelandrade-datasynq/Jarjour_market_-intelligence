$ErrorActionPreference = "Stop"

$Python = if (Test-Path ".\venv\Scripts\python.exe") {
    ".\venv\Scripts\python.exe"
} else {
    "python"
}

& $Python scripts\clean_workspace.py
& $Python -m ruff check . --no-cache
& $Python -m pytest -p no:cacheprovider
& $Python apps\server\manage.py check
& $Python apps\server\manage.py makemigrations --check --dry-run
& $Python scripts\run_quality_gates.py
& $Python scripts\clean_workspace.py
