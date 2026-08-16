import sys
import pymysql
from app import app
from config.web import DB_CONFIG
from services.contest_service import PawStarService

def test_e2e_existing_user_share_login_flow():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Failed")
        return

    with conn.cursor() as cur:
        # 진행 중인 콘테스트 라운드 1개 가져오기
        cur.execute("""
            SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN, r.ENT_USER_ID, COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT, COALESCE(r.SCORE, 0) AS SCORE
            FROM pst_contest_round r
            JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
            WHERE c.CONTEST_STAT = 'G001C001' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
            LIMIT 1
        """)
        target_post = cur.fetchone()

        if not target_post:
            print("No active contest round found for E2E test")
            conn.close()
            return

        c_round = target_post['CONTEST_ROUND']
        r_no = target_post['ROUND_NO']
        share_sn = target_post['SHARE_SN']
        owner_id = target_post['ENT_USER_ID']
        init_share_cnt = target_post['SHARE_CNT']
        init_score = target_post['SCORE']

        # 포스트 작성자가 아닌 기존 사용자 1명 선택
        cur.execute("SELECT USER_ID FROM pst_user WHERE USER_ID != %s LIMIT 1", (owner_id,))
        test_user = cur.fetchone()
        test_user_id = test_user['USER_ID']

        # 테스트용 이력 초기화
        cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
        conn.commit()

        print(f"[E2E TEST TARGET] Round {c_round}-{r_no}, SHARE_SN={share_sn}, User={test_user_id}")
        print(f"[INIT STATS] SHARE_CNT={init_share_cnt}, SCORE={init_score}")

        client = app.test_client()

        # STEP 1: 비로그인 상태로 공유 URL 접속 (/share)
        print("\n--- STEP 1: Visiting share URL as guest ---")
        share_resp = client.get(f"/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}")
        assert share_resp.status_code == 200, f"Share route failed: {share_resp.status_code}"

        # STEP 2: 기존 유저로 로그인 수행 (/api/auth/google 또는 /api/auth/login)
        print("--- STEP 2: Logging in as existing member ---")
        login_resp = client.post('/api/auth/google', json={
            'google_id': test_user_id.replace('google_', ''),
            'email': f"{test_user_id}@test.com",
            'name': 'TestExistingMember',
            'picture': '/static/image/profile/default_profile.png'
        })
        assert login_resp.status_code == 200, f"Google login failed: {login_resp.status_code}"

        # STEP 3: DB 상 점수 및 SHARE_CNT 증가 확인
        cur.execute("""
            SELECT COALESCE(SHARE_CNT, 0) AS SHARE_CNT, COALESCE(SCORE, 0) AS SCORE
            FROM pst_contest_round
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (c_round, r_no))
        after_post = cur.fetchone()

        print(f"[STEP 3 RESULT] SHARE_CNT: {after_post['SHARE_CNT']}, SCORE: {after_post['SCORE']}")
        assert after_post['SHARE_CNT'] == init_share_cnt + 1, f"Expected SHARE_CNT={init_share_cnt + 1}, got {after_post['SHARE_CNT']}"
        assert after_post['SCORE'] == init_score + 10, f"Expected SCORE={init_score + 10}, got {after_post['SCORE']}"

        # STEP 4: 이미 로그인된 상태에서 공유 URL 재방문 시 중복 차단 확인
        print("\n--- STEP 4: Re-visiting share URL while logged in (Duplicate protection) ---")
        share_resp2 = client.get(f"/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}")
        assert share_resp2.status_code == 200

        cur.execute("""
            SELECT COALESCE(SHARE_CNT, 0) AS SHARE_CNT, COALESCE(SCORE, 0) AS SCORE
            FROM pst_contest_round
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (c_round, r_no))
        after_post2 = cur.fetchone()
        print(f"[STEP 4 RESULT] SHARE_CNT: {after_post2['SHARE_CNT']} (No duplicate increase)")
        assert after_post2['SHARE_CNT'] == after_post['SHARE_CNT']

        # 데이터 정리 원복
        cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
        cur.execute("UPDATE pst_contest_round SET SHARE_CNT = %s, SCORE = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (init_share_cnt, init_score, c_round, r_no))
        conn.commit()
        print("\n[E2E TEST COMPLETED SUCCESSFULLY & DATA RESTORED]")

    conn.close()

if __name__ == '__main__':
    test_e2e_existing_user_share_login_flow()
