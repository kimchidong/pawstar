import sys
import unittest
sys.path.insert(0, '.')

from app import app
from services.contest_service import PawStarService

class TestShareButtonNavigation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.service = PawStarService()
        self.conn = self.service.get_db_connection()

    def tearDown(self):
        if self.conn:
            self.conn.close()

    def test_active_contest_button_href(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN
                FROM pst_contest_round r
                JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                WHERE c.CONTEST_STAT = 'G001C001' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
                LIMIT 1
            """)
            post = cur.fetchone()

        if not post:
            print("No active contest round found for testing")
            return

        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        share_sn = post['SHARE_SN']

        # PC 공유 페이지
        res_pc = self.app.get(f'/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res_pc.status_code, 200)
        html_pc = res_pc.data.decode('utf-8')
        expected_href_pc = f'/?open_post={c_round}_{r_no}'
        self.assertIn(expected_href_pc, html_pc, f"Expected {expected_href_pc} in PC share page")

        # 모바일 공유 페이지
        res_m = self.app.get(f'/m/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res_m.status_code, 200)
        html_m = res_m.data.decode('utf-8')
        expected_href_m = f'/m/?open_post={c_round}_{r_no}'
        self.assertIn(expected_href_m, html_m, f"Expected {expected_href_m} in Mobile share page")

        print("[SUCCESS] Active contest share page button links tested successfully!")

    def test_closed_contest_button_href(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT r.CONTEST_ROUND, r.ROUND_NO, r.SHARE_SN
                FROM pst_contest_round r
                JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                WHERE c.CONTEST_STAT = 'G001C002' AND r.SHARE_SN IS NOT NULL AND r.SHARE_SN != ''
                LIMIT 1
            """)
            post = cur.fetchone()

        if not post:
            print("No closed contest round found for testing, skipping closed test.")
            return

        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        share_sn = post['SHARE_SN']

        # PC 공유 페이지 (종료회차)
        res_pc = self.app.get(f'/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res_pc.status_code, 200)
        html_pc = res_pc.data.decode('utf-8')
        self.assertIn('href="/"', html_pc)
        self.assertNotIn(f'/?open_post={c_round}_{r_no}', html_pc)

        # 모바일 공유 페이지 (종료회차)
        res_m = self.app.get(f'/m/share?contest_round={c_round}&round_no={r_no}&share_sn={share_sn}')
        self.assertEqual(res_m.status_code, 200)
        html_m = res_m.data.decode('utf-8')
        self.assertIn('href="/m"', html_m)
        self.assertNotIn(f'/m/?open_post={c_round}_{r_no}', html_m)

        print("[SUCCESS] Closed contest share page button links tested successfully!")

if __name__ == '__main__':
    unittest.main()
