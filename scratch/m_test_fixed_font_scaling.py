import unittest

class TestMobileFixedFontScaling(unittest.TestCase):

    def test_m_style_css_text_size_adjust(self):
        with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('-webkit-text-size-adjust: 100% !important;', content)
        self.assertIn('text-size-adjust: 100% !important;', content)
        self.assertIn('@media screen and (orientation: landscape)', content)
        print("[PASS] m_style.css fixed text-size-adjust and landscape font locking verified!")

    def test_m_base_html_viewport_meta(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('shrink-to-fit=no', content)
        self.assertIn('css/m_style.css\') }}?v=20260901_130', content)
        print("[PASS] m_base.html viewport shrink-to-fit=no & cache buster v=20260901_130 verified!")

if __name__ == '__main__':
    unittest.main()
