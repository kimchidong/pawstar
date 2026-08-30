import unittest

class TestMobileAutoFillGrid(unittest.TestCase):

    def test_m_style_css_auto_fill_and_fixed_size(self):
        with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('repeat(auto-fill, minmax(194.22px, 1fr))', content)
        self.assertIn('width: 194.22px !important;', content)
        print("[PASS] m_style.css auto-fill maximum cards per row & 194.22px fixed size verified!")

    def test_m_base_html_css_version(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('css/m_style.css\') }}?v=20260901_110', content)
        print("[PASS] m_base.html m_style.css cache buster v=20260901_110 verified!")

if __name__ == '__main__':
    unittest.main()
