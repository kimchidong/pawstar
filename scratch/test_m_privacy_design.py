import unittest
from app import app

class TestMPrivacyDesign(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_m_privacy_page_renders_premium_design(self):
        res = self.app.get('/m/privacy')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        
        self.assertIn('PawStar 개인정보 처리 안내', html)
        self.assertIn('01', html)
        self.assertIn('08', html)
        self.assertIn('linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)', html)
        print("[SUCCESS] Mobile privacy premium design rendering verified successfully!")

if __name__ == '__main__':
    unittest.main()
