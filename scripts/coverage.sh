#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80 "$@"
