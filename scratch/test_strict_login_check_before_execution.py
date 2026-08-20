import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestStrictLoginCheckBeforeExecution(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_js_login_check(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. ensureLoggedIn helper defined
        self.assertIn('function ensureLoggedIn(onSuccess)', content)
        self.assertIn('window.ensureLoggedIn = ensureLoggedIn;', content)

        # 2. openDetailModal uses ensureLoggedIn
        self.assertIn('if (!ensureLoggedIn())', content)

    def test_m_main_js_login_check(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. ensureLoggedIn helper defined in m_main.js
        self.assertIn('function ensureLoggedIn(onSuccess)', content)
        self.assertIn('window.ensureLoggedIn = ensureLoggedIn;', content)

    def test_unauthenticated_page_redirect_with_login_flag(self):
        # 1. PC /upload route unauthenticated -> redirect to / with open_login=true
        res_upload = self.app.get('/upload')
        self.assertEqual(res_upload.status_code, 302)
        self.assertIn('open_login=true', res_upload.location)

        # 2. Mobile /m/upload route unauthenticated -> redirect to /m with open_login=true
        res_m_upload = self.app.get('/m/upload')
        self.assertEqual(res_m_upload.status_code, 302)
        self.assertIn('open_login=true', res_m_upload.location)

        # 3. /profile myprofile route unauthenticated -> redirect to / with open_login=true
        res_profile = self.app.get('/profile')
        self.assertEqual(res_profile.status_code, 302)
        self.assertIn('open_login=true', res_profile.location)

        # 4. /m/profile myprofile route unauthenticated -> redirect to /m with open_login=true
        res_m_profile = self.app.get('/m/profile')
        self.assertEqual(res_m_profile.status_code, 302)
        self.assertIn('open_login=true', res_m_profile.location)

if __name__ == '__main__':
    unittest.main()
