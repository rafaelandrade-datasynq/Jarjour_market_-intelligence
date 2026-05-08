.PHONY: install migrate seed run test lint check migration-check quality clean verify verify-clean

PYTHON ?= python
MANAGE = $(PYTHON) apps/server/manage.py

install:
	$(PYTHON) -m pip install -e ".[dev]"

migrate:
	$(MANAGE) migrate

seed:
	$(PYTHON) scripts/seed_demo_data.py

run:
	$(MANAGE) runserver 127.0.0.1:8000

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

check:
	$(MANAGE) check

migration-check:
	$(MANAGE) makemigrations --check --dry-run

quality:
	$(PYTHON) scripts/run_quality_gates.py

clean:
	$(PYTHON) scripts/clean_workspace.py

verify: lint test check migration-check quality

verify-clean: clean verify clean
