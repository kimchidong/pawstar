#!/bin/bash

# 환경 변수 설정
export APP_ENV=prd

APP_NAME="PawStar"
PORT=8003

# 실행 중인 프로세스가 있다면 메시지 출력 후 종료
PID=$(lsof -t -i:${PORT} -sTCP:LISTEN)

if [ -n "$PID" ]; then
    echo "$APP_NAME is already running on port $PORT (PID: $PID). Exiting."
    exit 1
fi

mkdir -p /svc/log/pawstar

# 백그라운드 실행 (nohup)
echo "Starting $APP_NAME in PRD environment..."

nohup bash -c "exec -a $APP_NAME python3 app.py" \
    > /dev/null 2>&1 &

echo "$APP_NAME started in background."