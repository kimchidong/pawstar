import pymysql
import uuid
from config import db_config
from services.contest_service import PawStarService

def test_share():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Failed")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, VW_CNT, LIKE_CNT, CMT_CNT, SHARE_CNT, SCORE, SHARE_SN FROM pst_contest_round LIMIT 1;")
        post = cur.fetchone()

        if not post:
            print("No test post found in pst_contest_round")
            conn.close()
            return

        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        initial_share = post['SHARE_CNT'] or 0
        initial_score = post['SCORE'] or 0

        print(f"=== Initial Post State ===")
        print(f"CONTEST_ROUND: {c_round}, ROUND_NO: {r_no}")
        print(f"VW: {post['VW_CNT']}, LIKE: {post['LIKE_CNT']}, CMT: {post['CMT_CNT']}, SHARE: {initial_share}, SCORE: {initial_score}")
        print(f"SHARE_SN: {post['SHARE_SN']}")

        # 1. get_or_create_share_sn 테스트
        share_sn = service.get_or_create_share_sn(c_round, r_no)
        print(f"\n[Test 1] Generated/Fetched SHARE_SN: {share_sn}")
        assert share_sn is not None and len(share_sn) > 0, "SHARE_SN generation failed"

        # 2. increment_share_count_on_signup 테스트 (공유 유입 회원가입 시)
        res = service.increment_share_count_on_signup(c_round, r_no, share_sn)
        print(f"\n[Test 2] Referral Signup Increment Result: {res}")
        assert res is True, "increment_share_count_on_signup failed"

        # 3. 최신화된 DB 수치 확인 (새 커밋 반영)
        conn.commit()
        cur.execute("SELECT VW_CNT, LIKE_CNT, CMT_CNT, SHARE_CNT, SCORE FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s;", (c_round, r_no))
        updated = cur.fetchone()
        
        expected_score = (updated['VW_CNT'] * 1) + (updated['LIKE_CNT'] * 5) + (updated['CMT_CNT'] * 10) + (updated['SHARE_CNT'] * 1)
        print(f"\n=== Updated Post State ===")
        print(f"VW: {updated['VW_CNT']}, LIKE: {updated['LIKE_CNT']}, CMT: {updated['CMT_CNT']}, SHARE: {updated['SHARE_CNT']}, SCORE: {updated['SCORE']}")
        print(f"Calculated 4-factor score: {expected_score}")

        assert updated['SHARE_CNT'] == initial_share + 1, f"SHARE_CNT mismatch: expected {initial_share + 1}, got {updated['SHARE_CNT']}"
        assert updated['SCORE'] == expected_score, f"SCORE mismatch: expected {expected_score}, got {updated['SCORE']}"

        print("\nAll SHARE tests passed successfully!")

    conn.close()

if __name__ == '__main__':
    test_share()
