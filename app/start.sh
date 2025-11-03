#!/usr/bin/env bash
set -euo pipefail

# Wait a touch for services (compose healthchecks already help)
sleep 1

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
