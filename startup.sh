#!/bin/bash
echo "Starting SHL Recommender API..."
exec uvicorn recommend_api:app --host 0.0.0.0 --port 10000
