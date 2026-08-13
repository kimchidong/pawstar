import unittest, os
from app import app

class TestEtcImagePath(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_image_file_exists(self):
        path1 = 'static/image/etc/preview_placeholder.jpg'
        path2 = 'static/image/etc/preview_default.jpg'
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
        print("[SUCCESS] Image files in static/image/etc verified!")

    def test_upload_page_uses_local_etc_image(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'user1'
        res = self.app.get('/upload')
        self.assertIn('/static/image/etc/preview_placeholder.jpg', res.data.decode('utf-8'))
        print("[SUCCESS] Upload template uses /static/image/etc/preview_placeholder.jpg!")

if __name__ == '__main__':
    unittest.main()
