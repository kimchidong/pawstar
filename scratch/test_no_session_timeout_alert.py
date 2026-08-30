import unittest

class TestNoSessionTimeoutAlert(unittest.TestCase):

    def test_main_js_no_inactivity_timer(self):
        with open('static/js/main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('initInactivityTimer', content)
        self.assertNotIn('30분 동안 활동이 없어 세션이 만료되었습니다', content)
        print("[PASS] main.js inactivity timer and session timeout alert completely removed!")

    def test_m_main_js_no_session_timeout_alert(self):
        with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('30분 동안 활동이 없어 세션이 만료되었습니다', content)
        print("[PASS] m_main.js no session timeout alert verified!")

if __name__ == '__main__':
    unittest.main()
