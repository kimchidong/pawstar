"""
Paw Star Entities
- Contest: 회차 정보 (CONTEST_ID, TITLE, START_DATE, END_DATE, STATUS)
- Post: 게시물 (POST_ID, USER_ID, CONTEST_ID, SCORE, VIEW, LIKE, COMMENT, SHARE)
- PostDailyStat: 일별 통계 (POST_ID, STAT_DATE, VIEW, LIKE, COMMENT, SHARE)
- ContestWinner: 수상 정보 (WINNER_ID, CONTEST_ID, POST_ID, USER_ID, AWARD_TYPE)
- User: 사용자 정보 (USER_ID, NICKNAME, PROFILE_IMG, etc.)
- Badge: 배지 및 이벤트 확장
"""

from datetime import datetime

class Contest:
    def __init__(self, contest_id, title, start_date, end_date, status='IN_PROGRESS', description='', banner_img=''):
        self.contest_id = contest_id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.status = status # 예정(SCHEDULED), 진행중(IN_PROGRESS), 종료(CLOSED)
        self.description = description
        self.banner_img = banner_img

    def to_dict(self):
        return {
            'contest_id': self.contest_id,
            'title': self.title,
            'start_date': str(self.start_date)[:10] if self.start_date else '',
            'end_date': str(self.end_date)[:10] if self.end_date else '',
            'status': self.status,
            'description': self.description,
            'banner_img': self.banner_img
        }

class Post:
    def __init__(self, post_id, user_id, contest_id, pet_name, pet_type, title, content, file_path, list_file_name, popup_file_name, media_type='IMAGE'):
        self.post_id = post_id
        self.user_id = user_id
        self.contest_id = contest_id
        self.pet_name = pet_name
        self.pet_type = pet_type # DOG, CAT, BIRD, etc.
        self.title = title
        self.content = content
        self.file_path = file_path
        self.list_file_name = list_file_name
        self.popup_file_name = popup_file_name
        self.media_type = media_type
        self.score = 0
        self.view_count = 0
        self.like_count = 0
        self.comment_count = 0
        self.share_count = 0
        self.created_at = datetime.now()

    def update_score(self, view_delta=0, like_delta=0, comment_delta=0, share_delta=0):
        self.view_count += view_delta
        self.like_count += like_delta
        self.comment_count += comment_delta
        self.share_count += share_delta
        
        # 이벤트 발생 시 score 계산: 조회+1, 좋아요+5, 댓글+10, 공유+1
        delta_score = (view_delta * 1) + (like_delta * 5) + (comment_delta * 10) + (share_delta * 1)
        self.score += delta_score
        return delta_score

class PostDailyStat:
    def __init__(self, post_id, stat_date):
        self.post_id = post_id
        self.stat_date = stat_date # YYYY-MM-DD
        self.view_count = 0
        self.like_count = 0
        self.comment_count = 0
        self.share_count = 0

    def add_activity(self, view=0, like=0, comment=0, share=0):
        self.view_count += view
        self.like_count += like
        self.comment_count += comment
        self.share_count += share

    def calculate_trending_score(self):
        # 최근 급상승 점수 : 조회x1, 좋아요x5, 댓글x10, 공유x1
        return (self.view_count * 1) + (self.like_count * 5) + (self.comment_count * 10) + (self.share_count * 1)

class ContestWinner:
    def __init__(self, winner_id, contest_id, post_id, user_id, award_type, prize_name=''):
        self.winner_id = winner_id
        self.contest_id = contest_id
        self.post_id = post_id
        self.user_id = user_id
        self.award_type = award_type # SUPER_STAR(1위), RISING_STAR(2위), BRIGHT_STAR(3위), ROOKIE_STAR(급상승 1위)
        self.prize_name = prize_name
        self.awarded_at = datetime.now()

class User:
    def __init__(self, user_id, nickname, profile_img, **kwargs):
        self.user_id = user_id
        self.nickname = nickname
        self.profile_img = profile_img
        self.badges = [] # 확장성: 보유 배지 목록
        self.awards = [] # 확장성: 프로필 수상 이력
