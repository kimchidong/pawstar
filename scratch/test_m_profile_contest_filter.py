import unittest
from app import app
from services.contest_service import PawStarService

class TestMProfileContestFilter(unittest.TestCase):
    def setUp(self):
        self.service = PawStarService()

    def test_get_user_profile_contest_filter(self):
        # 1. 전체 조회 테스트
        profile_all = self.service.get_user_profile('user1', contest_id='all')
        self.assertIn('user_info', profile_all)
        self.assertIn('my_posts', profile_all)
        self.assertIn('my_awards', profile_all)
        
        # 2. 특정 회차 조회 테스트 (ex: contest_id='1')
        profile_round1 = self.service.get_user_profile('user1', contest_id='1')
        for post in profile_round1['my_posts']:
            contest_round = str(post.get('CONTEST_ROUND') or post.get('contest_id'))
            self.assertEqual(contest_round, '1')
            
        for award in profile_round1['my_awards']:
            contest_round = str(award.get('CONTEST_ROUND') or award.get('contest_id'))
            self.assertEqual(contest_round, '1')

    def test_m_profile_template_render_with_tab_and_contest(self):
        with app.test_request_context('/m/profile?contest_id=1&tab=awards'):
            from flask import render_template
            mock_user = {'user_id': 'user1', 'nickname': '테스트집사', 'profile_img': '/static/image/profile/default_profile.png'}
            mock_stats = {'my_post_count': 1, 'total_score': 100, 'total_likes': 5, 'award_count': 1}
            mock_contests = [
                {'CONTEST_ROUND': 1, 'THEME_NM': '제1회 테마', 'CONTEST_STAT_NM': '종료'},
                {'CONTEST_ROUND': 2, 'THEME_NM': '제2회 테마', 'CONTEST_STAT_NM': '진행중'}
            ]
            
            rendered = render_template(
                'm_profile.html',
                user=mock_user,
                stats=mock_stats,
                my_posts=[],
                my_posts_pagination={'total_count': 0, 'page': 1, 'per_page': 10, 'total_pages': 1, 'has_prev': False, 'has_next': False},
                my_awards=[],
                contests=mock_contests,
                selected_contest_id='1'
            )
            
            self.assertIn('contest_id=1&amp;tab=awards', rendered)
            self.assertIn('선택하신 회차에는 출전한 게시물이 없습니다.', rendered)
            self.assertIn('선택하신 회차에는 수상 기록이 없습니다.', rendered)
            print("[SUCCESS] Mobile profile contest filter render test passed successfully!")

if __name__ == '__main__':
    import traceback
    try:
        t = TestMProfileContestFilter()
        t.setUp()
        t.test_get_user_profile_contest_filter()
        t.test_m_profile_template_render_with_tab_and_contest()
        print("ALL TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        traceback.print_exc()
