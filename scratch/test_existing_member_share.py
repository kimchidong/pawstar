import sys
import pymysql
import os
import importlib.util

def _get_config_web():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.web.py'),
        os.path.join(curr_dir, '..', 'config.web.py'),
        os.path.join(os.getcwd(), 'config.web.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_web", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.web.py 파일을 찾을 수 없습니다.")

config_web = _get_config_web()
DB_CONFIG = config_web.DB_CONFIG
from services.contest_service import PawStarService

def test_existing_member_share_referral():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB connection failed")
        return

    with conn.cursor() as cur:
        # 진행 중인 콘테스트 라운드 1개 조회
        cur.execute("""
            SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN, r.ENT_USER_ID, COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT, COALESCE(r.SCORE, 0) AS SCORE
            FROM pst_contest_round r
            JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
            WHERE c.CONTEST_STAT = 'G001C001' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
            LIMIT 1
        """)
        target_post = cur.fetchone()

        if not target_post:
            print("No active contest round found for testing.")
            conn.close()
            return

        c_round = target_post['CONTEST_ROUND']
        r_no = target_post['ROUND_NO']
        share_sn = target_post['SHARE_SN']
        owner_id = target_post['ENT_USER_ID']
        init_share_cnt = target_post['SHARE_CNT']
        init_score = target_post['SCORE']

        print(f"[TEST TARGET POST] Round {c_round}-{r_no}, SHARE_SN={share_sn}, Owner={owner_id}")
        print(f"[INIT STATS] SHARE_CNT: {init_share_cnt}, SCORE: {init_score}")

        # 포스트 작성자가 아닌 기존 회원 1명 선택
        cur.execute("SELECT USER_ID FROM pst_user WHERE USER_ID != %s LIMIT 1", (owner_id,))
        test_user = cur.fetchone()
        test_user_id = test_user['USER_ID'] if test_user else 'test_existing_member_99'

        # 혹시 기존 테스트 이력이 있으면 정리 (롤백 가능하게)
        cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
        conn.commit()

        # 1차 공유 유입 처리 테스트 (기존 회원 로그인/유입)
        print(f"\n[Test 1] Existing member '{test_user_id}' share referral test...")
        res1 = service.increment_share_count_on_signup(c_round, r_no, share_sn, user_id=test_user_id)
        assert res1 is True, "1st share referral failed"

        # 변경 후 DB 상태 확인
        cur.execute("""
            SELECT COALESCE(SHARE_CNT, 0) AS SHARE_CNT, COALESCE(SCORE, 0) AS SCORE
            FROM pst_contest_round
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (c_round, r_no))
        after_post1 = cur.fetchone()

        print(f"[1st REF SUCCESS] SHARE_CNT: {after_post1['SHARE_CNT']}, SCORE: {after_post1['SCORE']}")
        assert after_post1['SHARE_CNT'] == init_share_cnt + 1, "SHARE_CNT did not increment by 1"

        # 2차 중복 공유 유입 처리 테스트 (동일 유저 재로그인/재유입)
        print(f"\n[Test 2] Same member '{test_user_id}' duplicate referral test...")
        res2 = service.increment_share_count_on_signup(c_round, r_no, share_sn, user_id=test_user_id)
        assert res2 is False, "Duplicate referral was not blocked"

        # 2차 처리 후 상태 확인 (변화 없어야 함)
        cur.execute("""
            SELECT COALESCE(SHARE_CNT, 0) AS SHARE_CNT, COALESCE(SCORE, 0) AS SCORE
            FROM pst_contest_round
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (c_round, r_no))
        after_post2 = cur.fetchone()
        print(f"[2nd DUP BLOCKED] SHARE_CNT: {after_post2['SHARE_CNT']} (unchanged)")
        assert after_post2['SHARE_CNT'] == after_post1['SHARE_CNT'], "Duplicate score was incorrectly added"

        # 테스트용 생성 데이터 원복
        cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
        cur.execute("UPDATE pst_contest_round SET SHARE_CNT = %s, SCORE = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (init_share_cnt, init_score, c_round, r_no))
        conn.commit()
        print("\n[ALL TESTS PASSED & DATA RESTORED SUCCESSFULLY]")

    conn.close()

if __name__ == '__main__':
    test_existing_member_share_referral()
