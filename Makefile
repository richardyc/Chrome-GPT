.PHONY: tests lint lint_diff
PYTHON_FILES=.
lint: PYTHON_FILES=.
lint_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d master | grep -E '\.py$$')

lint lint_diff:
	poetry run mypy $(PYTHON_FILES)
	poetry run black $(PYTHON_FILES) --check --preview
	poetry run ruff .

format:
	poetry run black . --preview
	poetry run ruff . --fix

tests:
	poetry run pytest tests
