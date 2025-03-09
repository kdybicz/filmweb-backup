.PHONY: usage help setup clean .venv security_patch
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

test: test/unit

test/unit:
	pipenv run pytest

security_patch: SHELL:=/bin/bash
security_patch: setup
	pipenv run pipenv update
	pipenv run pipenv lock
