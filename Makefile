.PHONY: lint format-check typecheck test ci

PYTHON ?= python3

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy .

test:
	$(PYTHON) -m pytest -q

ci: lint format-check typecheck test
