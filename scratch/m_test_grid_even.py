import unittest

class TestMobileFixedSizeGrid(unittest.TestCase):

    def test_m_style_css_max_4_columns_and_fixed_size(self):
        with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('grid-template-columns: repeat(4, 194.22px) !important;', content)
        self.assertIn('width: 194.22px !important;', content)
        self.assertNotIn('repeat(6, 1fr)', content)
        print("[PASS] m_style.css max 4 columns and 194.22px fixed card size verified!")

    def test_m_base_html_css_version(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('css/m_style.css\') }}?v=20260901_105', content)
        print("[PASS] m_base.html m_style.css cache buster v=20260901_105 verified!")

if __name__ == '__main__':
    unittest.main()
