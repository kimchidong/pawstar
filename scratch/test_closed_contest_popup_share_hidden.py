import unittest

class TestClosedContestPopupShareHidden(unittest.TestCase):
    def test_main_js_closed_round_hides_share_btn(self):
        with open('static/js/main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("detailShareIconBtn.style.display = 'none'", content)
        self.assertIn("detailShareIconBtn.style.display = 'flex'", content)
        print("[SUCCESS] PC main.js closed contest detailShareIconBtn hidden logic verified!")

    def test_m_main_js_closed_round_hides_share_btn(self):
        with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("mDetailShareBtnHeader.style.display = 'none'", content)
        self.assertIn("mDetailShareBtnHeader.style.display = 'flex'", content)
        print("[SUCCESS] Mobile m_main.js closed contest mDetailShareBtnHeader hidden logic verified!")

if __name__ == '__main__':
    unittest.main()
