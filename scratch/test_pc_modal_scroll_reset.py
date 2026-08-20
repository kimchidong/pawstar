import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestPcModalScrollReset(unittest.TestCase):
    def test_main_js_pc_scroll_reset(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('function resetPcModalScroll()', content,
                      "main.js should contain resetPcModalScroll helper function")
        self.assertIn('resetPcModalScroll();', content,
                      "openDetailModal and closeDetailModal should call resetPcModalScroll")

if __name__ == '__main__':
    unittest.main()
