import unittest
from app import app

class TestMobileFooterLinks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_mobile_privacy_and_terms_urls(self):
        res_p = self.app.get('/m/privacy')
        self.assertEqual(res_p.status_code, 200)
        self.assertIn('개인정보 처리 안내', res_p.data.decode('utf-8'))
        
        res_t = self.app.get('/m/terms')
        self.assertEqual(res_t.status_code, 200)
        self.assertIn('PawStar 이용약관', res_t.data.decode('utf-8'))
        
        print("[SUCCESS] Mobile privacy and terms URLs tested successfully!")

if __name__ == '__main__':
    unittest.main()
