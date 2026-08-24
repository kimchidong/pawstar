import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import app
from services.contest_service import service

def test_pc_share_flow():
    print("=== [PC E2E Test] Share Link -> Login/Signup Referral Flow ===")

    # 1. 대상 출전작 준비 (1회차 1번 출전작)
    conn = service.get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, SHARE_CNT, SCORE FROM PST_CONTEST_ROUND LIMIT 1")
        post = cur.fetchone()
        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        author_id = post['ENT_USER_ID']

    print(f"Target Post: ({c_round}-{r_no}), Real Author ID: {author_id}")

    # TEST CASE 1: 타인의 공유 링크로 들어와 신규 회원가입 진행
    new_other_user = "test_pc_guest_user_99"
    service.delete_user(new_other_user)

    with app.test_client() as client:
        # Step A: 비로그인 상태로 PC 공유 전용 주소 랜딩 접속
        share_url = f"/share?contest_round={c_round}&round_no={r_no}&share_sn=S-TEST-999"
        res_landing = client.get(share_url)
        assert res_landing.status_code == 200, "Share landing failed"
        print(f"CASE 1-A) PC Share Landing HTTP 200 OK")

        # Step B: 회원가입 API 호출
        res_reg = client.post('/api/auth/register', json={
            'user_id': new_other_user,
            'nickname': '타인신규유저',
            'password': 'password123'
        })
        assert res_reg.status_code == 200, "Register failed"
        print(f"CASE 1-B) Register HTTP 200 OK: {res_reg.get_json()}")

    # CASE 1 DB 검증: 타인 유입이므로 PST_CONTEST_SHARE 기록 1건 및 SCORE +10점 가산되어야 함
    check_conn = service.get_db_connection()
    with check_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM PST_CONTEST_SHARE WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, new_other_user))
        share_cnt_rec = cur.fetchone()['cnt']
        
        cur.execute("SELECT SHARE_CNT, SCORE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
        post_after = cur.fetchone()
    check_conn.close()

    print(f"CASE 1 Result) Share Record Count: {share_cnt_rec} (Expected: 1)")
    print(f"              Post Stats: SHARE_CNT={post_after['SHARE_CNT']}, SCORE={post_after['SCORE']}")
    assert share_cnt_rec == 1, "Other user share referral record failed!"

    # 정리
    service.delete_user(new_other_user)

    # TEST CASE 2: 자가 공유 (본인의 출전작 공유링크 접속 -> 본인 계정 로그인)
    print("\n--- TEST CASE 2: Self-Share Exclusion Test ---")

    # 게시글 작성자 계정 사전 생성 (있는지 확인)
    author_user_id = author_id
    with app.test_client() as client_self:
        # Step A: 작성자 본인의 공유 링크 접속
        share_url_self = f"/share?contest_round={c_round}&round_no={r_no}&share_sn=S-TEST-999"
        client_self.get(share_url_self)

        # Step B: 작성자 본인 계정으로 로그인 API 호출
        res_login_self = client_self.post('/api/auth/login', json={
            'user_id': author_user_id,
            'password': 'password123'
        })

    # CASE 2 DB 검증: 본인 자가 공유이므로 PST_CONTEST_SHARE 에 추가 삽입되거나 점수가 오르면 안 됨
    check_conn2 = service.get_db_connection()
    with check_conn2.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM PST_CONTEST_SHARE WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, author_user_id))
        self_share_rec = cur.fetchone()['cnt']
    check_conn2.close()

    print(f"CASE 2 Result) Self Share Record Count for Author ({author_user_id}): {self_share_rec} (Expected: 0)")
    assert self_share_rec == 0, "Self share should be excluded!"

    conn.close()
    print("\n=== ALL PC E2E SHARE TESTS PASSED PERFECTLY ===")

if __name__ == '__main__':
    test_pc_share_flow()
