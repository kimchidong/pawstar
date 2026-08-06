import sys
import unittest
sys.path.insert(0, '.')

from app import app
from services.contest_service import PawStarService

class TestShare4ActionsActive(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.service = PawStarService()
        self.conn = self.service.get_db_connection()

    def tearDown(self):
        if self.conn:
            self.conn.close()

    def test_logged_in_share_landing_actions(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN, r.ENT_USER_ID, COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT
                FROM pst_contest_round r
                JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                WHERE c.CONTEST_STAT = 'G001C001' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
                LIMIT 1
            """)
            post = cur.fetchone()
            if not post:
                print("No active contest round found for testing")
                return

            # 포스트 작성자가 아닌 기존 유저 1명 선택
            cur.execute("SELECT USER_ID FROM pst_user WHERE USER_ID != %s LIMIT 1", (post['ENT_USER_ID'],))
            user = cur.fetchone()

        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        share_sn = post['SHARE_SN']
        test_user_id = user['USER_ID']

        # 해당 테스트 유저로 세션 로그인 설정 후 공유 페이지 접속
        with self.app.session_transaction() as sess:
            sess['user_id'] = test_user_id

        res = self.app.get(f'/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # 1. 로그인 유저 접속 시 곧바로 조회(btn-view)와 공유(btn-share) 요소가 active 클래스로 활성화되어 있는지 확인
        self.assertIn('btn-view active', html, "btn-view should have 'active' class when logged in user visits share page")
        self.assertIn('btn-share active', html, "btn-share should have 'active' class when logged in user visits share page")

        print("[SUCCESS] Logged in user share landing 4-actions active test passed!")

if __name__ == '__main__':
    unittest.main()
