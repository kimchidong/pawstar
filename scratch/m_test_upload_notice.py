import unittest

class TestMobileUploadNoticeAndConfirm(unittest.TestCase):
    def test_m_upload_notice_and_confirm(self):
        with open('templates/m_upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 통합 안내 카드 문구 확인
        self.assertIn('수정이 불가능하며 삭제만 가능', content)
        self.assertIn('수정 및 삭제 안내', content)
        
        # 2. confirm 팝업 코드 확인
        target_confirm = "confirm('콘테스트 출전 등록 후에는 수정이 불가능하며 삭제만 가능합니다. 출전하시겠습니까?')"
        self.assertIn(target_confirm, content)
        print("Mobile upload notice & confirm script verified successfully.")

if __name__ == '__main__':
    unittest.main()
