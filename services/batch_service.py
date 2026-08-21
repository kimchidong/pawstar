"""
Paw Star Batch Processing System
1. 점수 감점 배치
2. 회차 종료 및 수상자 선정 배치 (스타 1~3위 및 루키스타 1~3위)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from services.contest_service import service
from utils.logger import get_batch_logger, hash_ip

batch_logger = get_batch_logger()
LOCAL_HASH = hash_ip('127.0.0.1')
LOG_EXTRA = {'device': 'BATCH', 'ip_hash': LOCAL_HASH}

class PawStarBatchJob:

    @staticmethod
    def run_daily_decay_batch(decay_factor=0.95):
        """
        [배치 6] 점수 감소 배치
        오래된 게시물의 실시간 score를 일별 감점 인자(decay factor)를 적용하여 차감
        """
        batch_logger.info("Daily decay batch process started.", extra=LOG_EXTRA)
        count = 0
        for post in service.posts.values():
            old_score = post['score']
            post['score'] = max(0, int(old_score * decay_factor))
            count += 1
        batch_logger.info(f"Daily decay batch process completed. Updated {count} posts.", extra=LOG_EXTRA)
        return count

    @staticmethod
    def run_contest_close_and_award(contest_id):
        """
        [배치 10] 회차 종료 및 수상자 선정 배치
        """
        batch_logger.info(f"Contest close & award batch started for contest round #{contest_id}.", extra=LOG_EXTRA)
        winners = service.close_contest_and_award(contest_id)
        batch_logger.info(f"Contest close & award batch completed. Total winners awarded: {len(winners)}.", extra=LOG_EXTRA)
        return winners

if __name__ == '__main__':
    batch_logger.info("Batch service test execution started.", extra=LOG_EXTRA)
    PawStarBatchJob.run_daily_decay_batch()
    PawStarBatchJob.run_contest_close_and_award(3)
    batch_logger.info("Batch service test execution ended.", extra=LOG_EXTRA)
