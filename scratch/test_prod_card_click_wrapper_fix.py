import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestProdCardClickWrapperFix(unittest.TestCase):
    def test_main_js_handle_card_click_wrapper(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('async function handleCardClick(', content)
        self.assertIn('window.handleCardClick = handleCardClick;', content)

    def test_m_main_js_handle_mobile_card_click_wrapper(self):
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('async function handleMobileCardClick(', content)
        self.assertIn('window.handleMobileCardClick = handleMobileCardClick;', content)

    def test_templates_use_handle_card_click(self):
        index_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        self.assertIn('onclick="handleCardClick(', index_content)

        m_index_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'm_index.html')
        with open(m_index_path, 'r', encoding='utf-8') as f:
            m_index_content = f.read()
        self.assertIn('onclick="handleMobileCardClick(', m_index_content)

if __name__ == '__main__':
    unittest.main()
