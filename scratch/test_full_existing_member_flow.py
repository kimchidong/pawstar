import sys
import unittest
import json
import pymysql
sys.path.insert(0, '.')

from app import app
from services.contest_service import PawStarService

class TestExistingMemberShareFlow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.service = PawStarService()
        self.conn = self.service.get_db_connection()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN, r.ENT_USER_ID, COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT, COALESCE(r.SCORE, 0) AS SCORE
                FROM pst_contest_round r
                JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                WHERE c.CONTEST_STAT = 'G001C001' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
                LIMIT 1
            """)
            self.post = cur.fetchone()
            
            # 포스트 작성자가 아닌 기존 회원 1명
            cur.execute("SELECT USER_ID FROM pst_user WHERE USER_ID != %s LIMIT 1", (self.post['ENT_USER_ID'],))
            self.existing_user = cur.fetchone()

    def tearDown(self):
        if self.conn:
            self.conn.close()

    def test_existing_member_login_flow(self):
        if not self.post or not self.existing_user:
            print("No test data found")
            return

        c_round = self.post['CONTEST_ROUND']
        r_no = self.post['ROUND_NO']
        share_sn = self.post['SHARE_SN']
        test_user_id = self.existing_user['USER_ID']

        # 데이터 정리
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
            self.conn.commit()

        # 1. 비로그인 유저가 공유 페이지 /share 랜딩
        res1 = self.app.get(f'/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res1.status_code, 200)

        # 2. 공유 정보 세션 존재 하에 기존 회원 로그인 수행
        res2 = self.app.post('/api/auth/login', json={
            'user_id': test_user_id,
            'password': 'password123'
        })
        self.assertEqual(res2.status_code, 200)
        data = json.loads(res2.data)
        self.assertTrue(data['success'])

        # 3. DB 스탯 반영 확인
        with self.conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SHARE_CNT, 0) AS SHARE_CNT FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
            after_post = cur.fetchone()
            self.assertEqual(after_post['SHARE_CNT'], self.post['SHARE_CNT'] + 1)

            # 테스트용 기록 복원
            cur.execute("DELETE FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s", (c_round, r_no, test_user_id))
            cur.execute("UPDATE pst_contest_round SET SHARE_CNT = %s, SCORE = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (self.post['SHARE_CNT'], self.post['SCORE'], c_round, r_no))
            self.conn.commit()

        print("[SUCCESS] Existing member login share flow test passed successfully!")

if __name__ == '__main__':
    unittest.main()
