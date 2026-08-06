import sys
import unittest
sys.path.insert(0, '.')

from app import app

class TestUploadPreview4Actions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_preview_contains_4actions(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'

        # PC 출전 페이지
        res_pc = self.app.get('/upload')
        self.assertEqual(res_pc.status_code, 200)
        html_pc = res_pc.data.decode('utf-8')
        self.assertIn('btn-share', html_pc)
        self.assertIn('share-count', html_pc)

        # 모바일 출전 페이지
        res_m = self.app.get('/m/upload')
        self.assertEqual(res_m.status_code, 200)
        html_m = res_m.data.decode('utf-8')
        self.assertIn('btn-share', html_m)
        self.assertIn('repeat(4, 1fr)', html_m)

        print("[SUCCESS] Upload preview 4-actions test passed successfully!")

if __name__ == '__main__':
    unittest.main()
