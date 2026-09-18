# ViShield developer commands. Requires Python 3.11 (uv or pyenv recommended).
PY ?= python3.11
VENV ?= .venv
BIN := $(VENV)/bin
PORT_API ?= 8000
PORT_UI ?= 8501

.PHONY: help setup setup-uv install-stt demo-wav observability-up observability-down dashboard traffic run-api run-ui run test test-cov lint typecheck format \
        check audit data train evaluate docker-build docker-up docker-down clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Create .venv with pip and install package + dev extras
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"
	cp -n .env.example .env || true

setup-uv: ## Same as setup but using uv (faster)
	uv venv --python 3.11 $(VENV)
	uv pip install --python $(BIN)/python -e ".[dev]"
	cp -n .env.example .env || true

install-stt: ## Optional: local Whisper-compatible STT (downloads a model on first use)
	$(BIN)/pip install -e ".[stt]"

data: ## Validate dataset and regenerate splits
	$(BIN)/python scripts/validate_dataset.py
	$(BIN)/python scripts/split_dataset.py

train: ## Train the TF-IDF + logistic-regression baseline into models/
	$(BIN)/python scripts/train_model.py

evaluate: ## Evaluate rules, ML and hybrid on the held-out test split
	$(BIN)/python scripts/evaluate_model.py

demo-wav: ## Generate a 3 s synthetic (non-voice) demo.wav for upload demos
	$(BIN)/python -c "from tests.audio_fixtures import synthetic_speechlike, wav_bytes; open('demo.wav','wb').write(wav_bytes(synthetic_speechlike(3.0)))" && echo wrote demo.wav

run-api: ## Start FastAPI with auto-reload
	$(BIN)/uvicorn vishield.api.app:app --reload --port $(PORT_API)

run-ui: ## Start the Streamlit dashboard
	$(BIN)/streamlit run src/vishield/dashboard/app.py --server.port $(PORT_UI)

run: ## Start API and UI together (Ctrl-C stops both)
	$(MAKE) -j2 run-api run-ui

test: ## Run the test suite
	$(BIN)/pytest

test-cov: ## Run tests with coverage report
	$(BIN)/pytest --cov --cov-report=term-missing --cov-report=xml

lint: ## Ruff lint
	$(BIN)/ruff check .

format: ## Ruff format + autofix
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .

typecheck: ## mypy strict
	$(BIN)/mypy

audit: ## Dependency vulnerability audit
	$(BIN)/pip install --quiet --upgrade "setuptools>=83"
	$(BIN)/pip-audit --strict --desc --skip-editable

check: lint typecheck test ## Lint, typecheck and test

docker-build: ## Build the container image
	docker build -t vishield:local .

docker-up: ## Run API + dashboard via compose
	docker compose up --build

docker-down:
	docker compose down -v

observability-up: ## Start Alloy shipping /metrics to Grafana Cloud (needs observability/.env)
	docker compose -f observability/docker-compose.observability.yml --env-file observability/.env up -d

observability-down:
	docker compose -f observability/docker-compose.observability.yml --env-file observability/.env down

dashboard: ## Generate and push the Grafana dashboard (needs GRAFANA_URL + GRAFANA_SA_TOKEN)
	$(BIN)/python scripts/push_grafana_dashboard.py

traffic: ## Replay fictional transcripts through the API for 5 minutes to populate metrics
	$(BIN)/python scripts/generate_traffic.py --minutes 5

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml build dist *.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
