import unittest

class TestNoAuthorCardHover(unittest.TestCase):

    def test_base_html_no_hover(self):
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('onmouseover="this.style.transform', content)
        self.assertNotIn('onmouseout="this.style.transform', content)
        print("[PASS] base.html detailAuthorCard hover effect completely removed!")

    def test_m_base_html_no_hover(self):
        with open('templates/m_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('transition: transform 0.2s ease;', content)
        print("[PASS] m_base.html mDetailAuthorCard hover effect completely removed!")

if __name__ == '__main__':
    unittest.main()
