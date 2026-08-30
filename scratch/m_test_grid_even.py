import unittest

class TestMobileMin2ColsGrid(unittest.TestCase):

    def test_m_style_css_min_2_cols_and_4_3_aspect_ratio(self):
        with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('grid-template-columns: repeat(2, 1fr);', content)
        self.assertIn('aspect-ratio: 4 / 3 !important;', content)
        print("[PASS] m_style.css min 2 columns per row & 4:3 image aspect-ratio verified!")

    def test_m_base_html_css_version(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('css/m_style.css\') }}?v=20260901_120', content)
        print("[PASS] m_base.html m_style.css cache buster v=20260901_120 verified!")

if __name__ == '__main__':
    unittest.main()
