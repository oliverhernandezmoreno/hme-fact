#!/usr/bin/env bash
set -euo pipefail

docker-compose --profile test run --rm backend-test "$@"
