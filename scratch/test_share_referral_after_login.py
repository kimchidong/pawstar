import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import app
from services.contest_service import service

def test_share_referral_flow():
    print("=== Testing Share Referral Flow after Login/Signup ===")

    conn = service.get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, SHARE_CNT, SCORE FROM PST_CONTEST_ROUND LIMIT 1")
        post = cur.fetchone()
        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        author_id = post['ENT_USER_ID']

    # 자가 공유 방지를 위해 기존 작성자와 다른 유저 ID 생성
    test_user_id = f"new_signup_user_{c_round}_{r_no}_99"
    service.delete_user(test_user_id)

    with app.test_client() as client:
        # 1. 비로그인 상태로 공유 URL 접근
        share_url = f"/share?contest_round={c_round}&round_no={r_no}&share_sn=TEST_SHARE_SN_999"
        resp = client.get(share_url)
        print(f"1) Landing HTTP Status: {resp.status_code}")

        # 2. 비로그인 상태에서 회원가입 완료
        reg_resp = client.post('/api/auth/register', json={
            'user_id': test_user_id,
            'nickname': '공유신규유저',
            'password': 'password123'
        })
        print(f"2) Register response HTTP Status: {reg_resp.status_code}")

    # 3. 새로운 DB 커넥션으로 즉시 검증
    check_conn = service.get_db_connection()
    with check_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM PST_CONTEST_SHARE WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
        share_record = cur.fetchone()['cnt']
        
        cur.execute("SELECT SHARE_CNT, SCORE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
        after_post = cur.fetchone()

    print(f"3) Share DB Record Count for user '{test_user_id}': {share_record}")
    print(f"   Post stats after signup -> SHARE_CNT: {after_post['SHARE_CNT']}, SCORE: {after_post['SCORE']}")

    check_conn.close()
    conn.close()
    service.delete_user(test_user_id)
    print("=== Test Completed Cleanly ===")

if __name__ == '__main__':
    test_share_referral_flow()
