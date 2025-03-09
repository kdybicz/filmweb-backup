.PHONY: usage help setup clean .venv security_patch
.PHONY: format test/lint test/unit
.EXPORT_ALL_VARIABLES:

usage:
	@cat .usage
help: usage

clean:
	pipenv --rm || true

.venv: SHELL:=/bin/bash
.venv:
	pipenv install --dev --ignore-pipfile

setup: .venv

format:
	pipenv run isort --profile=black backup tests cli.py
	pipenv run black backup tests cli.py

test/lint:
	pipenv run black --diff --verbose --check backup/ tests/ cli.py
	# pipenv run pylint --output-format parseable backup/ tests/ cli.py
	pipenv run isort --profile=black --check-only backup/ tests/ cli.py

test: test/lint test/unit

test/unit:
	pipenv run pytest

security_patch: SHELL:=/bin/bash
security_patch: setup
	pipenv run pipenv update
	pipenv run pipenv lock
