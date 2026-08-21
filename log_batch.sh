#!/bin/bash
# Paw Star 운영 서버 배치 로그 조회 스크립트

LOG_DIR="${LOG_DIR:-/svc/log/pawstar/batch}"

if [ ! -d "$LOG_DIR" ] && [ -d "log/batch" ]; then
    LOG_DIR="log/batch"
fi

LATEST_LOG=$(ls -t "$LOG_DIR"/pawstar-batch.log* 2>/dev/null | head -n 1)

if [ -z "$LATEST_LOG" ]; then
    echo "[ERROR] 배치 로그 파일을 찾을 수 없습니다. (경로: $LOG_DIR)"
    exit 1
fi

echo "=================================================="
echo " PAW STAR 배치 로그 실시간 모니터링"
echo " Target File: $LATEST_LOG"
echo "=================================================="

tail -n 100 -f "$LATEST_LOG"
