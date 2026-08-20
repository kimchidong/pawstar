import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTemplateScriptTagValidity(unittest.TestCase):
    def test_base_html_script_tags(self):
        html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check window.isUserLoggedIn is wrapped inside <script> tag
        target = "window.isUserLoggedIn = "
        idx = content.find(target)
        self.assertNotEqual(idx, -1, "window.isUserLoggedIn should exist in base.html")

        # Looking back for <script>
        script_before = content.rfind('<script', 0, idx)
        script_close_before = content.rfind('</script>', 0, idx)

        self.assertTrue(script_before > script_close_before, "window.isUserLoggedIn must be inside a <script> block")

    def test_m_base_html_script_tags(self):
        html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'm_base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        target = "window.isUserLoggedIn = "
        idx = content.find(target)
        self.assertNotEqual(idx, -1, "window.isUserLoggedIn should exist in m_base.html")

        script_before = content.rfind('<script', 0, idx)
        script_close_before = content.rfind('</script>', 0, idx)

        self.assertTrue(script_before > script_close_before, "window.isUserLoggedIn must be inside a <script> block in m_base.html")

if __name__ == '__main__':
    unittest.main()
