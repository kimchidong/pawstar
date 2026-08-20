import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestShareBadgeActive(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_js_content(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. openPostById default parameter check (should be false)
        self.assertIn('function openPostById(postId, isHallOfFame = false)', content,
                      "openPostById default isHallOfFame parameter should be false")

        # 2. checkAndAutoOpenPost should check path and pass isHOFPage
        self.assertIn('const isHOFPage = window.location.pathname.includes(\'hall-of-fame\');', content,
                      "checkAndAutoOpenPost should check if current page is hall-of-fame")
        self.assertIn('openPostById(openPostId, isHOFPage);', content,
                      "checkAndAutoOpenPost should pass isHOFPage to openPostById")

        # 3. updatePcContestBadgeUI pIsClosed check
        self.assertIn('const pIsClosed = isClosedRound;', content,
                      "updatePcContestBadgeUI pIsClosed should be synchronized with isClosedRound")

    def test_share_detail_html_link(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'share_detail.html')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check CTA link contains open_post parameter
        self.assertIn('open_post=', content, "share_detail.html CTA link should contain open_post parameter")

if __name__ == '__main__':
    unittest.main()
