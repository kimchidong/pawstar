import unittest

class TestFooter3StarsFill(unittest.TestCase):

    def test_base_html_3_stars_fill(self):
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('for rk in [1, 2, 3]', content)
        self.assertIn('aspect-ratio: 4 / 3;', content)
        print("[PASS] base.html 3 stars fill and 4:3 aspect ratio verified!")

    def test_m_base_html_3_stars_fill(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('for rk in [1, 2, 3]', content)
        self.assertIn('aspect-ratio: 4 / 3;', content)
        print("[PASS] m_base.html 3 stars fill and 4:3 aspect ratio verified!")

if __name__ == '__main__':
    unittest.main()
