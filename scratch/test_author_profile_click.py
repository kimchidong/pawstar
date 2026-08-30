import unittest

class TestAuthorProfileClick(unittest.TestCase):

    def test_base_html_author_card_click(self):
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="detailAuthorCard" onclick="goToAuthorProfile();"', content)
        print("[PASS] base.html detailAuthorCard onclick verified!")

    def test_m_base_html_author_card_click(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="mDetailAuthorCard" onclick="goToMobileAuthorProfile();"', content)
        print("[PASS] m_base.html mDetailAuthorCard onclick verified!")

    def test_main_js_goto_profile(self):
        with open('static/js/main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('window.goToAuthorProfile = function()', content)
        self.assertIn('window.currentDetailAuthorId =', content)
        print("[PASS] main.js goToAuthorProfile verified!")

    def test_m_main_js_goto_profile(self):
        with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('window.goToMobileAuthorProfile = function()', content)
        self.assertIn('window.currentMobileDetailAuthorId =', content)
        print("[PASS] m_main.js goToMobileAuthorProfile verified!")

if __name__ == '__main__':
    unittest.main()
