import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestSessionTimeoutCheck(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_check_session_api_unauthenticated(self):
        # 1. 미로그인 세션 상태에서 API 호출 시 logged_in: False 응답
        res = self.app.get('/api/auth/check-session')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data['logged_in'])
        self.assertEqual(data['reason'], 'session_expired')

    def test_check_session_api_authenticated(self):
        # 2. 로그인 세션 주입 후 API 호출 시 logged_in: True 응답
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'test_user_99'

        res = self.app.get('/api/auth/check-session')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['logged_in'])
        self.assertEqual(data['user_id'], 'test_user_99')

    def test_js_verify_server_session_async_presence(self):
        main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(main_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('async function verifyServerSessionAsync()', content)
        self.assertIn('await verifyServerSessionAsync();', content)

        m_main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(m_main_js_path, 'r', encoding='utf-8') as f:
            m_content = f.read()

        self.assertIn('async function verifyServerSessionAsync()', m_content)
        self.assertIn('await verifyServerSessionAsync();', m_content)

if __name__ == '__main__':
    unittest.main()
