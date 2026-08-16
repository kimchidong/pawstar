#!/bin/bash

export APP_ENV=prd

mkdir -p /svc/log/pawstar

echo "Starting PawStar in PRD environment..."

exec python3 app.py