
PYTHON := python3
VENV := .venv
PYTHON_VENV := $(VENV)/bin/python
.DEFAULT_GOAL := help

.PHONY: help setup install run clean

help:
	@echo "Available commands:"
	@echo "  make setup    - Create environment and install dependencies"
	@echo "  make install  - Install project dependencies"
	@echo "  make run      - Run the main Python program"
	@echo "  make clean    - Remove virtual environment"

setup:
	$(PYTHON) -m venv $(VENV)
	$(MAKE) install

install:
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt

run:
	$(PYTHON_VENV) TwoRandomMovers.py

clean:
	rm -rf $(VENV)
