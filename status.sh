#!/bin/bash

PORT=8003
APP_DIR="/svc/app/pawstar"
APP_NAME="PawStar"

PIDS=$(lsof -t -i:${PORT} -sTCP:LISTEN)

if [ -z "$PIDS" ]; then
    echo "$APP_NAME is NOT running."
    exit 1
fi

echo "$APP_NAME is running."
echo ""

for PID in $PIDS; do
    CMD=$(ps -p "$PID" -o args=)
    DIR=$(readlink -f /proc/$PID/cwd 2>/dev/null)

    echo "PID : $PID"
    echo "CMD : $CMD"
    echo "DIR : $DIR"
    echo ""

    ps -fp "$PID"
    echo ""
done