import unittest

class TestPcUploadNotice(unittest.TestCase):
    def test_pc_upload_notice_contained(self):
        with open('templates/upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('수정이 불가능하며 삭제만 가능', content)
        self.assertIn('수정 및 삭제 안내', content)
        print("PC upload unified notice card verified successfully.")

if __name__ == '__main__':
    unittest.main()
