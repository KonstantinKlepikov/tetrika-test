#! /usr/bin/env bash
set -e

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-config /log.ini --reload-dir /app