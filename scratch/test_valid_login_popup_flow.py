import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestValidLoginPopupFlow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_check_session_api_for_authenticated_user(self):
        # 1. Authentic session test
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'valid_user_123'

        res = self.app.get('/api/auth/check-session')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['logged_in'], "Valid logged in session must return logged_in: True")
        self.assertEqual(data['user_id'], 'valid_user_123')

    def test_verify_server_session_async_restores_logged_in_state(self):
        main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(main_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if verifyServerSessionAsync sets window.isUserLoggedIn = true when server returns logged_in: true
        self.assertIn('window.isUserLoggedIn = true;', content)
        self.assertIn("localStorage.removeItem('pawstar_logged_out')", content)

if __name__ == '__main__':
    unittest.main()
