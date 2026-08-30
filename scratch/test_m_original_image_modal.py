import unittest

class TestGalaxyTabDetailModal(unittest.TestCase):

    def test_m_base_html_img_events(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('openOriginalImageModal(this.src)', content)
        self.assertIn('ontouchstart=', content)
        print("[PASS] m_base.html mDetailImg touch and click handlers verified!")

    def test_m_main_js_ytb_player_and_z_index(self):
        with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('imgEl.style.zIndex = \'35\'', content)
        self.assertIn('window[playerKey] = new YT.Player', content)
        print("[PASS] m_main.js z-index 35 and YT.Player initialization verified!")

if __name__ == '__main__':
    unittest.main()
