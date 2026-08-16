#!/bin/bash

PORT=8003
APP_DIR="/svc/app/pawstar"
APP_NAME="PawStar"

PID=$(lsof -t -i:${PORT} -sTCP:LISTEN)

if [ -z "$PID" ]; then
    echo "$APP_NAME is NOT running."
    exit 1
fi

CMD=$(ps -p "$PID" -o args=)

echo "$APP_NAME is running."
echo "PID : $PID"
echo "CMD : $CMD"
echo "DIR : $(readlink -f /proc/$PID/cwd)"
echo ""

ps -fp "$PID"