#!/bin/bash

echo "Restarting ToolMong..."

# 기존 프로세스 중지
./stop.sh

# 프로세스가 완전히 종료될 시간을 벌기 위해 잠시 대기
sleep 1

# 새로운 프로세스 시작
./start.sh

echo "ToolMong restart complete."
