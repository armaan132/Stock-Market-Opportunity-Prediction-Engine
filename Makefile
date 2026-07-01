.PHONY: setup train app test lint clean

PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip setuptools wheel
	$(BIN)/python -m pip install -r requirements.txt
	$(BIN)/python -m pip install -e .

train:
	$(BIN)/market-opportunity train

app:
	$(BIN)/streamlit run app/streamlit_app.py

test:
	$(BIN)/python -m pytest -q

lint:
	$(BIN)/python -m ruff check .

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
