#!/bin/bash
echo "Starting SHL Recommender API..."
exec uvicorn recommender_api:app --host 0.0.0.0 --port 10000
