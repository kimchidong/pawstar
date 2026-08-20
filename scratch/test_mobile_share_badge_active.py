import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestMobileShareBadgeActive(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_m_main_js_content(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. openPostById default parameter check (should be false)
        self.assertIn('function openPostById(postId, isHallOfFame = false)', content,
                      "m_main.js openPostById default isHallOfFame parameter should be false")

        # 2. checkAndAutoOpenMobilePost should check path and pass isHOFPage
        self.assertIn('const isHOFPage = window.location.pathname.includes(\'hall-of-fame\');', content,
                      "checkAndAutoOpenMobilePost should check if current page is hall-of-fame")

        # 3. Mobile Scroll reset check
        self.assertIn('const mScrollBody = detailModal.querySelector(\'.m-modal-scroll-body\');', content,
                      "openMobileDetailModal should reset m-modal-scroll-body scrollTop")
        self.assertIn('if (mScrollBody) mScrollBody.scrollTop = 0;', content,
                      "closeMobileDetailModal / openMobileDetailModal should set mScrollBody scrollTop to 0")

if __name__ == '__main__':
    unittest.main()
