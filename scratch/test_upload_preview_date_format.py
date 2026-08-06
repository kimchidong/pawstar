import sys
import re
import unittest
sys.path.insert(0, '.')

from app import app

class TestUploadPreviewDateFormat(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_preview_date_format(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'

        res_pc = self.app.get('/upload')
        self.assertEqual(res_pc.status_code, 200)
        html_pc = res_pc.data.decode('utf-8')

        # '방금 전' 이 previewCardDate에 포함되지 않는지 확인
        self.assertNotIn('방금 전', html_pc)

        # YYYY-MM-DD HH:mm:ss 형태의 날짜 정규식 검증
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        self.assertTrue(bool(date_pattern.search(html_pc)), "HTML should contain YYYY-MM-DD HH:mm:ss formatted date string")

        print("[SUCCESS] Upload preview date format YYYY-MM-DD HH:mm:ss tested successfully!")

if __name__ == '__main__':
    unittest.main()
