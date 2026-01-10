.PHONY: setup clean test lint format prepare-release docker-build

PYTHON = python3.12
VENV = .venv
BIN = $(VENV)/bin

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .[dev]
	$(BIN)/pip install pre-commit
	$(BIN)/pre-commit install --install-hooks

clean:
	$(BIN)/pre-commit uninstall
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

test:
	$(BIN)/pytest

lint:
	$(BIN)/flake8
	$(BIN)/black --check .
	$(BIN)/isort --check .

bandit:
	$(BIN)/bandit -r ./ecosystems_cli

black:
	$(BIN)/black ./ecosystems_cli
	$(BIN)/black ./tests

isort:
	$(BIN)/isort ./ecosystems_cli
	$(BIN)/isort ./tests

fix-all:
	$(BIN)/isort ./ecosystems_cli
	$(BIN)/isort ./tests
	$(BIN)/flake8 ./ecosystems_cli
	$(BIN)/flake8 ./tests
	$(BIN)/black ./ecosystems_cli
	$(BIN)/black ./tests

complexipy:
	$(BIN)/complexipy ./ecosystems_cli

format:
	$(BIN)/black .
	$(BIN)/isort .

docker-build:
	docker build -t ecosystems-cli:dev .
