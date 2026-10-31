#!/usr/bin/env bash
# Усі статичні перевірки (те саме запускає CI). Автовиправлення: ruff check --fix . && ruff format .
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -x .venv/bin/ruff ]; then PATH="$PWD/.venv/bin:$PATH"; fi

ruff check .                          # лінтер: pyflakes, pep8-naming, bugbear, імпорти, pytest-style
ruff format --check .                 # форматування (порожні рядки, пробіли, переноси за PEP 8)
pycodestyle --config=.pycodestyle .   # PEP 8
python scripts/check_test_style.py    # без логіки в тестах
