import unittest
from app import app

class TestUploadPetOption(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_page_contains_pet_option_js(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'user1'
        res = self.app.get('/upload')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn('selectUploadPetOption', html)
        self.assertIn("typeof e.preventDefault === 'function'", html)
        print("[SUCCESS] Upload pet option JS fix verified successfully!")

if __name__ == '__main__':
    unittest.main()
