import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMultiTabLogoutSync(unittest.TestCase):
    def test_main_js_multi_tab_sync(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Real-time cookie checker function exists
        self.assertIn('function checkCurrentLoginCookie()', content)

        # 2. ensureLoggedIn verifies checkCurrentLoginCookie and pawstar_logged_out storage flag
        self.assertIn('const hasCookie = checkCurrentLoginCookie();', content)
        self.assertIn('const hasStorageLogout = localStorage.getItem(\'pawstar_logged_out\') === \'true\';', content)

        # 3. Storage event listener registered for multi-tab logout broadcast
        self.assertIn('window.addEventListener(\'storage\'', content)

    def test_m_main_js_multi_tab_sync(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('function checkCurrentLoginCookie()', content)
        self.assertIn('const hasCookie = checkCurrentLoginCookie();', content)
        self.assertIn('window.addEventListener(\'storage\'', content)

if __name__ == '__main__':
    unittest.main()
