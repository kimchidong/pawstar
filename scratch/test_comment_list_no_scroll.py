import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestCommentListNoScroll(unittest.TestCase):
    def test_pc_base_html_comment_list(self):
        html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('id="detailCommentList" style="display: flex; flex-direction: column; gap: 0.5rem;"', content,
                      "PC base.html detailCommentList should not have max-height or overflow-y limit")

    def test_mobile_base_html_comment_list(self):
        html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'm_base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('id="mDetailCommentList" style="display: flex; flex-direction: column; gap: 0.5rem;"', content,
                      "Mobile m_base.html mDetailCommentList should not have max-height or overflow-y limit")

if __name__ == '__main__':
    unittest.main()
