import pymysql
import uuid
from config import db_config
from services.contest_service import PawStarService

def test_pst_contest_share_integration():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Fail")
        return

    test_user_id = f"test_share_user_{uuid.uuid4().hex[:6]}"
    c_round = 1
    r_no = 1
    
    with conn.cursor() as cur:
        # 게시물의 SHARE_SN 조회
        cur.execute("SELECT SHARE_SN FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s;", (c_round, r_no))
        row = cur.fetchone()
        share_sn = row['SHARE_SN']

        # 1. 공유 유입 회원가입 시 PST_CONTEST_SHARE 저장 및 증가 테스트
        res = service.increment_share_count_on_signup(c_round, r_no, share_sn, user_id=test_user_id)
        assert res is True, "increment_share_count_on_signup failed"

        # 2. PST_CONTEST_SHARE 레코드 존재 여부 검증 (커밋 후 스냅샷 갱신)
        conn.commit()
        cur.execute("SELECT * FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s;", (c_round, r_no, test_user_id))
        share_record = cur.fetchone()
        assert share_record is not None, f"PST_CONTEST_SHARE record not found for user {test_user_id}"
        print(f"1. PST_CONTEST_SHARE INSERT verified: {share_record}")

        # 3. 해당 유저가 조회 시 actions['is_shared']가 True로 반환되는지 검증
        post_detail = service.get_post_detail(c_round, r_no, current_user_id=test_user_id)
        assert post_detail is not None, "get_post_detail returned None"
        assert post_detail.get('actions', {}).get('is_shared') is True, f"actions['is_shared'] should be True, got {post_detail.get('actions')}"
        print("2. User actions is_shared == True verified successfully!")

    conn.close()
    print("\nAll PST_CONTEST_SHARE tests passed cleanly!")

if __name__ == '__main__':
    test_pst_contest_share_integration()
