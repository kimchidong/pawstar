import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMobileTitleInContentBox(unittest.TestCase):
    def test_m_base_html_structure(self):
        html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'm_base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # mDetailContentBox should wrap mDetailTitle
        box_idx = content.find('id="mDetailContentBox"')
        title_idx = content.find('id="mDetailTitle"')
        content_idx = content.find('id="mDetailContent"')

        self.assertNotEqual(box_idx, -1, "mDetailContentBox should exist")
        self.assertNotEqual(title_idx, -1, "mDetailTitle should exist")
        self.assertNotEqual(content_idx, -1, "mDetailContent should exist")

        self.assertTrue(box_idx < title_idx < content_idx, "mDetailTitle and mDetailContent should both be inside mDetailContentBox")

    def test_m_main_js_title_handling(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('mContentBox.style.display = (titleText || contentText) ? \'block\' : \'none\';', content,
                      "mDetailContentBox should be visible if either titleText or contentText exists")

if __name__ == '__main__':
    unittest.main()
