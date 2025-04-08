#!/bin/bash

# Activate virtual env if needed (optional on Railway)
echo "Running startup script..."
uvicorn recommender_api:app --host 0.0.0.0 --port $PORT
