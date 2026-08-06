import sys
import unittest

class TestDropdownBorderCSS(unittest.TestCase):
    def test_css_in_progress_dropdown_border(self):
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()

        # stat-in-progress 드롭다운 트리거의 테두리가 #e2e8f0 로 적용되어 있는지 확인
        self.assertIn('.custom-contest-dropdown.stat-in-progress .custom-contest-trigger {\n    background: #fefce8;\n    border: 1.5px solid #e2e8f0;', css_content)
        self.assertIn('.custom-contest-dropdown.stat-in-progress .custom-contest-trigger:hover {\n    background: #fef9c3;\n    border-color: #cbd5e1;', css_content)
        print("[SUCCESS] CSS dropdown border color test passed successfully!")

if __name__ == '__main__':
    unittest.main()
