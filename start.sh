#!/bin/bash

# 환경 변수 설정
export APP_ENV=prd

# 실행 중인 프로세스가 있다면 메시지 출력 후 종료 (포트 8003 기준)
PID=$(lsof -t -i:8003)

if [ ! -z "$PID" ]; then
    echo "PawStar is already running on port 8003 (PID: $PID). Exiting."
    exit 1
fi

# 로그 디렉토리 생성 (config.py의 prd 설정 반영)
mkdir -p /svc/log/pawstar

# 백그라운드 실행 (nohup)
echo "Starting PawStar in PRD environment..."

nohup python3 app.py > /dev/null 2>&1 &

echo "PawStar started in background."
