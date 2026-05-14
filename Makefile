.PHONY: test test-unit test-integration test-e2e coverage lint format docker-test docker-test-unit docker-test-integration install-dev

PYTEST ?= pytest
DOCKER_COMPOSE ?= docker-compose
VENV ?= .venv
PYTHON ?= python3

install-dev:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements-dev.txt

test:
	$(PYTEST)

test-unit:
	$(PYTEST) -m unit tests/unit --no-cov

test-integration:
	$(PYTEST) -m integration tests/integration --no-cov

test-e2e:
	$(PYTEST) -m e2e tests/e2e --no-cov

coverage:
	$(PYTEST) --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80

lint:
	ruff check app tests

format:
	ruff format app tests
	ruff check --fix app tests

docker-test:
	$(DOCKER_COMPOSE) --profile test run --rm backend-test

docker-test-unit:
	$(DOCKER_COMPOSE) --profile test run --rm backend-test pytest -m unit tests/unit --no-cov

docker-test-integration:
	$(DOCKER_COMPOSE) --profile test run --rm backend-test pytest -m integration tests/integration --no-cov
