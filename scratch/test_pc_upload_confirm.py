import unittest

class TestPcUploadConfirm(unittest.TestCase):
    def test_pc_upload_confirm_contained(self):
        with open('templates/upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        target_str = "confirm('콘테스트 출전 등록 후에는 수정이 불가능하며 삭제만 가능합니다. 출전하시겠습니까?')"
        self.assertIn(target_str, content)
        print("PC upload form submit confirm script verified successfully.")

if __name__ == '__main__':
    unittest.main()
