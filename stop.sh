#!/bin/bash

# 실행 중인 프로세스 확인 (포트 8001 기준)
PID=$(lsof -t -i:8001)

if [ -z "$PID" ]; then
    echo "ToolMong is not running on port 8001."
else
    echo "Stopping ToolMong (PID: $PID)..."
    kill $PID
    
    # 프로세스가 종료될 때까지 잠시 대기
    sleep 2
    
    # 여전히 실행 중인지 확인
    PID_RECHECK=$(lsof -t -i:8001)
    if [ ! -z "$PID_RECHECK" ]; then
        echo "Process did not stop, forcing termination..."
        kill -9 $PID_RECHECK
    fi
    echo "ToolMong stopped."
fi
