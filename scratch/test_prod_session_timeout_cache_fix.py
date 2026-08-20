import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestProdSessionTimeoutCacheFix(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_check_session_cache_headers(self):
        # 1. /api/auth/check-session returns no-cache headers for prod proxy servers
        res = self.app.get('/api/auth/check-session')
        self.assertEqual(res.status_code, 200)
        cache_header = res.headers.get('Cache-Control', '')
        self.assertIn('no-cache', cache_header)
        self.assertIn('no-store', cache_header)
        self.assertIn('must-revalidate', cache_header)

    def test_js_timestamp_query_param(self):
        # 2. main.js and m_main.js include timestamp query ?t= to bypass browser & proxy cache
        main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(main_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("'/api/auth/check-session?t=' + Date.now()", content)

        m_main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(m_main_js_path, 'r', encoding='utf-8') as f:
            m_content = f.read()
        self.assertIn("'/api/auth/check-session?t=' + Date.now()", m_content)

if __name__ == '__main__':
    unittest.main()
