import pymysql
import uuid
from config import db_config
from services.contest_service import PawStarService

def test_share_active_rule():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Error")
        return

    c_round = 1
    r_no = 1
    
    # 1. 일반 회원 (공유 가입 X)
    normal_user_id = f"normal_user_{uuid.uuid4().hex[:6]}"
    
    # 2. 공유 가입 회원
    shared_user_id = f"shared_user_{uuid.uuid4().hex[:6]}"

    with conn.cursor() as cur:
        # SHARE_SN 가져오기
        cur.execute("SELECT SHARE_SN FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s;", (c_round, r_no))
        row = cur.fetchone()
        share_sn = row['SHARE_SN']

        # shared_user_id 만 공유가입 처리
        service.increment_share_count_on_signup(c_round, r_no, share_sn, user_id=shared_user_id)
        conn.commit()

        # 검증 1: 일반 유저가 볼 때 -> actions['is_shared'] == False (비활성화 상태)
        normal_detail = service.get_post_detail(c_round, r_no, current_user_id=normal_user_id)
        assert normal_detail.get('actions', {}).get('is_shared') is False, f"Normal user should see is_shared == False, got {normal_detail.get('actions')}"
        print("1. Normal user sees is_shared == False (INACTIVE) verified!")

        # 검증 2: 비회원(None)이 볼 때 -> actions['is_shared'] == False (비활성화 상태)
        anon_detail = service.get_post_detail(c_round, r_no, current_user_id=None)
        assert anon_detail.get('actions', {}).get('is_shared') is False, f"Anonymous user should see is_shared == False, got {anon_detail.get('actions')}"
        print("2. Anonymous user sees is_shared == False (INACTIVE) verified!")

        # 검증 3: 공유 가입 유저가 볼 때 -> actions['is_shared'] == True (활성화 상태)
        shared_detail = service.get_post_detail(c_round, r_no, current_user_id=shared_user_id)
        assert shared_detail.get('actions', {}).get('is_shared') is True, f"Shared user should see is_shared == True, got {shared_detail.get('actions')}"
        print("3. Shared referral user sees is_shared == True (ACTIVE) verified!")

    conn.close()
    print("\nAll share active rule tests passed 100% cleanly!")

if __name__ == '__main__':
    test_share_active_rule()
