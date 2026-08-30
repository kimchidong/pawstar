import unittest

class TestShowImageButton(unittest.TestCase):

    def test_base_html_show_image_btn(self):
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="detailShowImgBtn"', content)
        self.assertIn("showPostImage('pc')", content)
        print("[PASS] base.html detailShowImgBtn verified!")

    def test_m_base_html_show_image_btn(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="mDetailShowImgBtn"', content)
        self.assertIn("showPostImage('mobile')", content)
        self.assertIn('z-index: 60;', content)
        self.assertIn('pointer-events: auto !important;', content)
        print("[PASS] m_base.html mDetailShowImgBtn verified!")

    def test_upload_html_show_image_btn(self):
        with open('templates/upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="previewShowImgBtn"', content)
        self.assertIn("showPostImage('preview_pc')", content)
        print("[PASS] upload.html previewShowImgBtn verified!")

    def test_m_upload_html_show_image_btn(self):
        with open('templates/m_upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('id="mPreviewShowImgBtn"', content)
        self.assertIn("showPostImage('preview_mobile')", content)
        self.assertIn('z-index: 60;', content)
        self.assertIn('pointer-events: auto !important;', content)
        print("[PASS] m_upload.html mPreviewShowImgBtn verified!")

    def test_main_js_show_post_image_func(self):
        with open('static/js/main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function showPostImage(type)', content)
        self.assertIn('window.showPostImage = showPostImage', content)
        print("[PASS] main.js showPostImage function verified!")

    def test_m_main_js_show_post_image_func(self):
        with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function showPostImage(type)', content)
        self.assertIn('window.showPostImage = showPostImage', content)
        print("[PASS] m_main.js showPostImage function verified!")

if __name__ == '__main__':
    unittest.main()
