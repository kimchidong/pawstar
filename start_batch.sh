#!/bin/bash

# 환경 변수 설정 (운영 환경: prd)
export APP_ENV=prd

# 작업 디렉토리 이동
APP_DIR="/svc/app/pawstar"
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR
fi

# 로그 디렉토리 생성
mkdir -p /svc/log/pawstar

echo "Starting Monthly Award Batch in PRD environment..."

# monthly_award_batch.py 실행 및 로그 파일 출력
python3 monthly_award_batch.py >> /svc/log/pawstar/batch.log 2>&1

echo "Monthly Award Batch completed."
