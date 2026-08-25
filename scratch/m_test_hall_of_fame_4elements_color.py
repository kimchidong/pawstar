import unittest

class TestMobileHallOfFame4ElementsColor(unittest.TestCase):
    def test_m_hall_of_fame_4elements_color_applied(self):
        with open('templates/m_hall_of_fame.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 활성화/비활성화 시 아이콘 및 컬러 분기 스타일 적용 확인
        self.assertIn("#0284c7' if is_view_act else '#94a3b8'", content)
        self.assertIn("#e11d48' if is_like_act else '#94a3b8'", content)
        self.assertIn("#7c3aed' if is_cmt_act else '#94a3b8'", content)
        self.assertIn("#15803d' if is_share_act else '#94a3b8'", content)
        
        # 2. FontAwesome 아이콘 변환 적용 확인
        self.assertIn("fa-eye", content)
        self.assertIn("fa-heart", content)
        self.assertIn("fa-comment", content)
        self.assertIn("fa-share-nodes", content)
        
        print("Mobile Hall of Fame 4-elements active/inactive color styling verified successfully.")

if __name__ == '__main__':
    unittest.main()
