"""
Paw Star Batch Processing System
1. 점수 감점 배치
2. 회차 종료 및 수상자 선정 배치 (스타 1~3위 및 루키스타 1~3위)
"""

from datetime import datetime, timedelta
from services.contest_service import service

class PawStarBatchJob:

    @staticmethod
    def run_daily_decay_batch(decay_factor=0.95):
        """
        [배치 6] 점수 감소 배치
        오래된 게시물의 실시간 score를 일별 감점 인자(decay factor)를 적용하여 차감
        """
        print(f"[{datetime.now()}] 🔄 점수 감소(Decay) 배치 실행...")
        count = 0
        for post in service.posts.values():
            old_score = post['score']
            post['score'] = max(0, int(old_score * decay_factor))
            count += 1
        print(f"[{datetime.now()}] ✅ 총 {count}개 게시물의 점수가 감점 조정되었습니다.")
        return count

    @staticmethod
    def run_contest_close_and_award(contest_id):
        """
        [배치 10] 회차 종료 및 수상자 선정 배치
        1위: SUPER_STAR
        2위: RISING_STAR
        3위: BRIGHT_STAR
        급상승 1위(1~3위 제외): ROOKIE_STAR
        """
        print(f"[{datetime.now()}] 🏆 제{contest_id}회 콘테스트 회차 종료 및 수상자 선정 배치 시작...")
        winners = service.close_contest_and_award(contest_id)
        print(f"[{datetime.now()}] ✅ 수상자 {len(winners)}명 선정 완료:")
        for w in winners:
            print(f"  - [{w['award_type']}] 게시물ID: {w['post_id']}, 반려동물: {w['pet_name']}, 집사: {w['user_nickname']}")
        return winners

if __name__ == '__main__':
    # 배치 테스트 실행
    print("=== Paw Star 배치 시스템 테스트 ===")
    PawStarBatchJob.run_daily_decay_batch()
    PawStarBatchJob.run_contest_close_and_award(3)
