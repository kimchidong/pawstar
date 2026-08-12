import unittest
from app import app

class TestLivePreviewSync(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_page_contains_live_preview_selectors(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'user1'
        res = self.app.get('/upload')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        
        self.assertIn('id="uploadPetName"', html)
        self.assertIn('id="uploadTitle"', html)
        self.assertIn('querySelector(\'input[name="pet_name"]\')', html)
        self.assertIn('querySelector(\'input[name="title"]\')', html)
        print("[SUCCESS] Live preview element selectors verified successfully!")

if __name__ == '__main__':
    unittest.main()
