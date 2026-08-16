#!/bin/bash

export APP_ENV=prd

mkdir -p /svc/log/toolmong

echo "Starting ToolMong in PRD environment..."

exec python3 app.py