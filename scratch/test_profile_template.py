import unittest
from app import app

class TestProfileTemplate(unittest.TestCase):
    def test_profile_template_render(self):
        with app.test_request_context('/profile'):
            from flask import render_template
            mock_user = {'user_id': 'user1', 'nickname': '테스트', 'profile_img': ''}
            mock_stats = {'my_post_count': 1, 'total_score': 10, 'total_likes': 5}
            mock_contests = [
                {'CONTEST_ROUND': 9, 'THEME_NM': '한여름 밤의 바캉스 펫 챔피언십', 'CONTEST_STAT_NM': '진행중', 'status': '진행중'},
                {'CONTEST_ROUND': 8, 'THEME_NM': '한여름 밤의 바캉스 펫 챔피언십', 'CONTEST_STAT_NM': '종료', 'status': '종료'}
            ]
            
            rendered = render_template(
                'profile.html',
                user=mock_user,
                stats=mock_stats,
                my_posts=[],
                my_awards=[],
                contests=mock_contests,
                selected_contest_id='all'
            )
            
            self.assertIn('진행중', rendered)
            self.assertIn('제 9회', rendered)
            print("[SUCCESS] Profile template render test with Flask context passed successfully!")

if __name__ == '__main__':
    unittest.main()
