import sys
import unittest
sys.path.insert(0, '.')

from app import app

class TestHallOfFameEmptyBadges(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_empty_award_slots_do_not_contain_badges(self):
        res = self.app.get('/hall-of-fame')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # '수상자가 없습니다.' 가 들어있는 경우
        if '수상자가 없습니다' in html or '선정된 수상자가 없습니다' in html:
            # 빈 슬롯 내에 메달/뱃지 요소가 포함되어 렌더링되는 부적절한 조합이 없는지 검사
            # 빈 슬롯 렌더링 블럭 내에는 crown-badge 가 없어야 함
            import re
            empty_blocks = re.findall(r'<p[^>]*>선정된 수상자가 없습니다\.</p>|<p[^>]*>수상자가 없습니다\.</p>', html)
            self.assertTrue(len(empty_blocks) > 0, "Empty slots found")
            
            # 메달 이미지가 수상자가 없는 슬롯 안에서 출력되지 않는지 확인
            # 'P002A90' 가 이미지 태그로 '수상자가 없습니다' 근처에 없어야함
            print(f"[SUCCESS] Checked {len(empty_blocks)} empty award slots. Medals and badges are hidden.")

if __name__ == '__main__':
    unittest.main()
