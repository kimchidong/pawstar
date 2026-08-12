import unittest
from app import app

class TestUploadRedirect(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_post_redirects_to_main_page(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'user1'
        
        response = self.app.post('/upload', data={
            'title': '테스트 자랑 제목',
            'content': '테스트 자랑 내용',
            'pet_name': '초코',
            'pet_type': '🐕 강아지'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/?uploaded=true', response.location)
        print("[SUCCESS] Desktop upload redirect to main page tested successfully!")

    def test_m_upload_post_redirects_to_m_main_page(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'user1'
            
        response = self.app.post('/m/upload', data={
            'title': '모바일 테스트 자랑 제목',
            'content': '모바일 테스트 자랑 내용',
            'pet_name': '나비',
            'pet_type': '🐈 고양이'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/m?uploaded=true', response.location)
        print("[SUCCESS] Mobile upload redirect to m_main page tested successfully!")

if __name__ == '__main__':
    unittest.main()
