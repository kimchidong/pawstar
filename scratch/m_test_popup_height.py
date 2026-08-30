import unittest

class TestMobilePopupHeight(unittest.TestCase):

    def test_m_base_html_popup_height(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('max-height: 82vh;', content)
        self.assertNotIn('max-height: 92vh;', content)
        print("[PASS] m_base.html mDetailModal max-height 82vh verified!")

    def test_m_upload_html_popup_height(self):
        with open('templates/m_upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('max-height: 82vh;', content)
        self.assertNotIn('max-height: 92vh;', content)
        print("[PASS] m_upload.html mPreviewModalBackdrop max-height 82vh verified!")

    def test_m_style_css_popup_height(self):
        with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('max-height: 82vh;', content)
        self.assertIn('max-height: calc(82vh - 68px);', content)
        print("[PASS] m_style.css .m-modal-sheet and .m-modal-scroll-body max-height 82vh verified!")

if __name__ == '__main__':
    unittest.main()
