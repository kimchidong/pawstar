"""
Paw Star Contest & Ranking Service
"""

from datetime import datetime, timedelta
import random

class PawStarService:
    def __init__(self):
        # 데모 퍼블리싱용 메모리 데이터 스토어 (데이터베이스가 세팅 안된 환경에서도 완벽 시연 가능)
        self.contests = {}
        self.posts = {}
        self.daily_stats = [] # list of dicts: {'post_id', 'stat_date', 'view', 'like', 'comment', 'share'}
        self.winners = [] # list of dicts: {'contest_id', 'post_id', 'user_id', 'award_type', 'prize_name'}
        self.users = {}
        
        self._init_mock_data()

    def _init_mock_data(self):
        """ 초기 퍼블리싱 시연용 샘플 데이터 세팅 """
        # Users (plamodelshop 호환 구조)
        self.users['user1'] = {
            'user_id': 'user1',
            'nickname': '뽀삐아빠',
            'profile_img': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80',
            'bio': '골든리트리버 뽀삐와 함께 살고 있습니다 🦮',
            'badges': ['🥇 1회 슈퍼스타', '⭐ 급상승 루키']
        }
        self.users['user2'] = {
            'user_id': 'user2',
            'nickname': '냥냥 집사',
            'profile_img': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=200&q=80',
            'bio': '귀여운 아비시니안 나비의 일상 🐈',
            'badges': ['🥈 2회 라이징스타']
        }
        self.users['user3'] = {
            'user_id': 'user3',
            'nickname': '햄찌마스터',
            'profile_img': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=200&q=80',
            'bio': '볼빵빵 햄찌 모찌 🐹',
            'badges': ['🥉 1회 브라이트스타']
        }
        self.users['user4'] = {
            'user_id': 'user4',
            'nickname': '앵두네',
            'profile_img': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80',
            'bio': '노래하는 모란앵무 앵두 🦜',
            'badges': ['⭐ 2회 루키스타']
        }

        # Contests
        self.contests[3] = {
            'contest_id': 3,
            'title': '제3회 Paw Star 콘테스트',
            'start_date': '2026-07-01',
            'end_date': '2026-07-31',
            'status': '진행중',
            'description': '세상에서 가장 사랑스러운 우리 아이의 심쿵 모먼트! 🌟 대한민국 대표 펫 스타에 도전하세요!'
        }
        self.contests[2] = {
            'contest_id': 2,
            'title': '제2회 Paw Star 콘테스트',
            'start_date': '2026-06-01',
            'end_date': '2026-06-30',
            'status': '종료',
            'description': '매일이 매력 폭발! 최고의 펫 스타를 가리는 콘테스트 🌟'
        }
        self.contests[1] = {
            'contest_id': 1,
            'title': '제1회 Paw Star 콘테스트',
            'start_date': '2026-05-01',
            'end_date': '2026-05-31',
            'status': '종료',
            'description': 'Paw Star 대망의 개막 1회 콘테스트 🎉'
        }

        # Posts for Contest #3 (진행중)
        sample_posts = [
            {
                'post_id': 101,
                'user_id': 'user1',
                'contest_id': 3,
                'pet_name': '뽀삐',
                'pet_type': '🐕 강아지',
                'title': '웃는 모습이 너무 예쁜 우리 뽀삐 자랑해요!',
                'content': '오늘 잔디밭 산책 다녀왔는데 기분이 너무 좋은지 햇살 아래서 천사처럼 웃네요 💕 다들 뽀삐 웃음 보고 힐링하세요!',
                'media_url': 'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=800&q=80',
                'media_type': 'IMAGE',
                'score': 1580,
                'view_count': 320,
                'like_count': 112,
                'comment_count': 40,
                'share_count': 15,
                'created_at': '2026-07-10 14:20:00'
            },
            {
                'post_id': 102,
                'user_id': 'user2',
                'contest_id': 3,
                'pet_name': '나비',
                'pet_type': '🐈 고양이',
                'title': '박스만 보면 일단 들어가고 보는 나비의 하루',
                'content': '택배 박스 뜯자마자 식빵 굽기 완성! 이 굴뚝같은 귀여움 어쩌죠? 🐾',
                'media_url': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
                'media_type': 'IMAGE',
                'score': 1420,
                'view_count': 410,
                'like_count': 90,
                'comment_count': 32,
                'share_count': 12,
                'created_at': '2026-07-12 10:15:00'
            },
            {
                'post_id': 103,
                'user_id': 'user3',
                'contest_id': 3,
                'pet_name': '모찌',
                'pet_type': '🐹 햄스터',
                'title': '볼따구에 해바라기씨 10개 저장 성공!',
                'content': '볼이 터질 것 같은 볼빵빵 모찌입니다. 귀여운 먹방 구경오세요~',
                'media_url': 'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&w=800&q=80',
                'media_type': 'IMAGE',
                'score': 1890,
                'view_count': 590,
                'like_count': 130,
                'comment_count': 45,
                'share_count': 10,
                'created_at': '2026-07-15 18:30:00'
            },
            {
                'post_id': 104,
                'user_id': 'user4',
                'contest_id': 3,
                'pet_name': '앵두',
                'pet_type': '🦜 앵무새',
                'title': '주인 껌딱지 앵두의 헤드뱅잉 장기자랑',
                'content': '신나는 음악 틀어주면 박자에 맞춰서 날개를 흔드는 흥부자 앵두랍니다 🎶',
                'media_url': 'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80',
                'media_type': 'IMAGE',
                'score': 1210,
                'view_count': 260,
                'like_count': 80,
                'comment_count': 25,
                'share_count': 15,
                'created_at': '2026-07-18 09:00:00'
            }
        ]

        for p in sample_posts:
            self.posts[p['post_id']] = p

        # 30일간의 POST_DAILY_STAT 데이터 시뮬레이션 생성
        today = datetime.now().date()
        for post_id in self.posts:
            for i in range(30):
                stat_date = str(today - timedelta(days=i))
                v = random.randint(5, 30)
                l = random.randint(1, 10)
                c = random.randint(0, 4)
                s = random.randint(0, 2)
                self.daily_stats.append({
                    'post_id': post_id,
                    'stat_date': stat_date,
                    'view_count': v,
                    'like_count': l,
                    'comment_count': c,
                    'share_count': s
                })

        # 제2회 종료 회차 명예의 전당 수상자 데이터 세팅
        self.winners.append({
            'contest_id': 2,
            'post_id': 201,
            'user_id': 'user2',
            'award_type': 'SUPER_STAR', # 🥇 1위
            'prize_name': '🥇 Paw Star 골드 트로피 & 백화점 상품권 50만원',
            'pet_name': '나비',
            'pet_type': '🐈 고양이',
            'post_title': '식빵 굽기 세계 챔피언 나비',
            'media_url': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
            'score': 3450,
            'user_nickname': '냥냥 집사',
            'user_profile': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=200&q=80'
        })
        self.winners.append({
            'contest_id': 2,
            'post_id': 202,
            'user_id': 'user1',
            'award_type': 'RISING_STAR', # 🥈 2위
            'prize_name': '🥈 Paw Star 실버 트로피 & 펫 용품 30만원',
            'pet_name': '뽀삐',
            'pet_type': '🐕 강아지',
            'post_title': '개구쟁이 뽀삐의 흙놀이 샷',
            'media_url': 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
            'score': 2980,
            'user_nickname': '뽀삐아빠',
            'user_profile': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
        })
        self.winners.append({
            'contest_id': 2,
            'post_id': 203,
            'user_id': 'user3',
            'award_type': 'BRIGHT_STAR', # 🥉 3위
            'prize_name': '🥉 Paw Star 브론즈 트로피 & 프리미엄 사료 세트',
            'pet_name': '모찌',
            'pet_type': '🐹 햄스터',
            'post_title': '쳇바퀴 100km 돌파 순간',
            'media_url': 'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&w=800&q=80',
            'score': 2410,
            'user_nickname': '햄찌마스터',
            'user_profile': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=200&q=80'
        })
        self.winners.append({
            'contest_id': 2,
            'post_id': 204,
            'user_id': 'user4',
            'award_type': 'ROOKIE_STAR', # ⭐ 급상승 1위 (루키스타)
            'prize_name': '⭐ 루키 스타 특별 배지 & 백화점 10만원 상품권',
            'pet_name': '앵두',
            'pet_type': '🦜 앵무새',
            'post_title': '하루만에 조회수 5천 돌파 앵두 댄스',
            'media_url': 'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80',
            'score': 2100,
            'user_nickname': '앵두네',
            'user_profile': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80'
        })

    # --- 조회 및 정렬 기능 ---

    def _attach_d_day(self, contest):
        if not contest:
            return None
        c = dict(contest)
        try:
            end_dt = datetime.strptime(c['end_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            diff = (end_dt - today).days
            if diff > 0:
                c['d_day_str'] = f"D-{diff}"
            elif diff == 0:
                c['d_day_str'] = "D-DAY"
            else:
                c['d_day_str'] = "종료됨"
        except Exception:
            c['d_day_str'] = "D-Day"
        return c

    def get_contests(self):
        c_list = sorted(list(self.contests.values()), key=lambda x: x['contest_id'], reverse=True)
        return [self._attach_d_day(c) for c in c_list]

    def get_contest(self, contest_id):
        return self._attach_d_day(self.contests.get(int(contest_id)))

    def get_posts(self, contest_id=3, sort_type='latest', search_query=''):
        """
        sort_type:
        - 'latest': 최신 등록순 ORDER BY created_at DESC (기본값)
        - 'popular': 인기순 ORDER BY score DESC
        - 'trending': 최근 급상승 (30일 일별 통계 점수 합산)
        """
        contest_id = int(contest_id)
        filtered = [p for p in self.posts.values() if p['contest_id'] == contest_id]

        if search_query:
            q = search_query.lower()
            filtered = [p for p in filtered if q in p['title'].lower() or q in p['pet_name'].lower() or q in p['content'].lower()]

        # 작성자 정보 결합
        result = []
        for p in filtered:
            item = dict(p)
            user_info = self.users.get(p['user_id'], {})
            item['user_nickname'] = user_info.get('nickname', '익명')
            item['user_profile'] = user_info.get('profile_img', '')
            
            # 최근 30일 급상승 점수 계산
            trending_score = self._calculate_30day_trending_score(p['post_id'])
            item['trending_score'] = trending_score

            # 수상 내역 여부
            item['badges'] = user_info.get('badges', [])
            result.append(item)

        # 정렬 수행
        if sort_type == 'popular':
            result.sort(key=lambda x: x['score'], reverse=True)
        elif sort_type == 'trending':
            result.sort(key=lambda x: x['trending_score'], reverse=True)
        elif sort_type == 'latest':
            result.sort(key=lambda x: x['created_at'], reverse=True)

        return result

    def _calculate_30day_trending_score(self, post_id):
        today = datetime.now().date()
        date_limit = str(today - timedelta(days=30))
        
        sum_view, sum_like, sum_comment, sum_share = 0, 0, 0, 0
        for ds in self.daily_stats:
            if ds['post_id'] == post_id and ds['stat_date'] >= date_limit:
                sum_view += ds['view_count']
                sum_like += ds['like_count']
                sum_comment += ds['comment_count']
                sum_share += ds['share_count']
        
        # 급상승 공식: 조회*1 + 좋아요*5 + 댓글*10 + 공유*20
        return (sum_view * 1) + (sum_like * 5) + (sum_comment * 10) + (sum_share * 20)

    def trigger_event(self, post_id, event_type):
        """
        이벤트 발생시 실시간 score 증가
        - 조회: +1
        - 좋아요: +5
        - 댓글: +10
        - 공유유입: +20
        """
        post_id = int(post_id)
        if post_id not in self.posts:
            return None

        post = self.posts[post_id]
        today_str = str(datetime.now().date())

        v_delta, l_delta, c_delta, s_delta = 0, 0, 0, 0
        if event_type == 'view':
            v_delta = 1
            post['view_count'] += 1
        elif event_type == 'like':
            l_delta = 1
            post['like_count'] += 1
        elif event_type == 'comment':
            c_delta = 1
            post['comment_count'] += 1
        elif event_type == 'share':
            s_delta = 1
            post['share_count'] += 1

        delta_score = (v_delta * 1) + (l_delta * 5) + (c_delta * 10) + (s_delta * 20)
        post['score'] += delta_score

        # 일별 통계 테이블 (POST_DAILY_STAT) 기록/업데이트
        stat_entry = next((item for item in self.daily_stats if item['post_id'] == post_id and item['stat_date'] == today_str), None)
        if not stat_entry:
            stat_entry = {
                'post_id': post_id,
                'stat_date': today_str,
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'share_count': 0
            }
            self.daily_stats.append(stat_entry)

        stat_entry['view_count'] += v_delta
        stat_entry['like_count'] += l_delta
        stat_entry['comment_count'] += c_delta
        stat_entry['share_count'] += s_delta

        return {
            'post_id': post_id,
            'new_score': post['score'],
            'delta_score': delta_score,
            'view_count': post['view_count'],
            'like_count': post['like_count'],
            'comment_count': post['comment_count'],
            'share_count': post['share_count']
        }

    def get_hall_of_fame(self, contest_id=2):
        """ 회차별 1~3위 (SUPER, RISING, BRIGHT) 및 급상승 1위 (ROOKIE) 조회 """
        contest_id = int(contest_id)
        contest_winners = [w for w in self.winners if w['contest_id'] == contest_id]
        
        # 순서 정렬 (SUPER -> RISING -> BRIGHT -> ROOKIE)
        order_map = {'SUPER_STAR': 1, 'RISING_STAR': 2, 'BRIGHT_STAR': 3, 'ROOKIE_STAR': 4}
        contest_winners.sort(key=lambda x: order_map.get(x['award_type'], 99))
        return contest_winners

    def close_contest_and_award(self, contest_id):
        """ 회차 종료 및 수상자 자동 선정 배치 """
        contest_id = int(contest_id)
        if contest_id in self.contests:
            self.contests[contest_id]['status'] = '종료'

        # 해당 회차 게시물들 점수순 정렬
        contest_posts = [p for p in self.posts.values() if p['contest_id'] == contest_id]
        contest_posts.sort(key=lambda x: x['score'], reverse=True)

        if not contest_posts:
            return []

        # 기존 수상 내역 제거 후 새로 배치 수행
        self.winners = [w for w in self.winners if w['contest_id'] != contest_id]

        new_winners = []
        # 1위 SUPER_STAR
        if len(contest_posts) >= 1:
            p = contest_posts[0]
            u = self.users.get(p['user_id'], {})
            w1 = {
                'contest_id': contest_id,
                'post_id': p['post_id'],
                'user_id': p['user_id'],
                'award_type': 'SUPER_STAR',
                'prize_name': '🥇 Paw Star 골드 트로피 & 백화점 상품권 50만원',
                'pet_name': p['pet_name'],
                'pet_type': p['pet_type'],
                'post_title': p['title'],
                'media_url': p['media_url'],
                'score': p['score'],
                'user_nickname': u.get('nickname', ''),
                'user_profile': u.get('profile_img', '')
            }
            new_winners.append(w1)
            self.winners.append(w1)

        # 2위 RISING_STAR
        if len(contest_posts) >= 2:
            p = contest_posts[1]
            u = self.users.get(p['user_id'], {})
            w2 = {
                'contest_id': contest_id,
                'post_id': p['post_id'],
                'user_id': p['user_id'],
                'award_type': 'RISING_STAR',
                'prize_name': '🥈 Paw Star 실버 트로피 & 펫 용품 30만원',
                'pet_name': p['pet_name'],
                'pet_type': p['pet_type'],
                'post_title': p['title'],
                'media_url': p['media_url'],
                'score': p['score'],
                'user_nickname': u.get('nickname', ''),
                'user_profile': u.get('profile_img', '')
            }
            new_winners.append(w2)
            self.winners.append(w2)

        # 3위 BRIGHT_STAR
        if len(contest_posts) >= 3:
            p = contest_posts[2]
            u = self.users.get(p['user_id'], {})
            w3 = {
                'contest_id': contest_id,
                'post_id': p['post_id'],
                'user_id': p['user_id'],
                'award_type': 'BRIGHT_STAR',
                'prize_name': '🥉 Paw Star 브론즈 트로피 & 프리미엄 사료 세트',
                'pet_name': p['pet_name'],
                'pet_type': p['pet_type'],
                'post_title': p['title'],
                'media_url': p['media_url'],
                'score': p['score'],
                'user_nickname': u.get('nickname', ''),
                'user_profile': u.get('profile_img', '')
            }
            new_winners.append(w3)
            self.winners.append(w3)

        # 급상승 1위 ROOKIE_STAR (1~3위 제외한 게시물 중 급상승 점수가 가장 높은 게시물)
        top_3_ids = [w['post_id'] for w in new_winners]
        remaining_posts = [p for p in contest_posts if p['post_id'] not in top_3_ids]
        
        if remaining_posts:
            # 급상승 점수로 정렬
            remaining_posts.sort(key=lambda x: self._calculate_30day_trending_score(x['post_id']), reverse=True)
            rookie_post = remaining_posts[0]
            u = self.users.get(rookie_post['user_id'], {})
            rookie_winner = {
                'contest_id': contest_id,
                'post_id': rookie_post['post_id'],
                'user_id': rookie_post['user_id'],
                'award_type': 'ROOKIE_STAR',
                'prize_name': '⭐ 루키 스타 특별 배지 & 백화점 10만원 상품권',
                'pet_name': rookie_post['pet_name'],
                'pet_type': rookie_post['pet_type'],
                'post_title': rookie_post['title'],
                'media_url': rookie_post['media_url'],
                'score': rookie_post['score'],
                'user_nickname': u.get('nickname', ''),
                'user_profile': u.get('profile_img', '')
            }
            new_winners.append(rookie_winner)
            self.winners.append(rookie_winner)

        return new_winners

    def create_post(self, contest_id, user_id, pet_name, pet_type, title, content, media_url):
        post_id = max(self.posts.keys(), default=100) + 1
        new_post = {
            'post_id': post_id,
            'user_id': user_id,
            'contest_id': int(contest_id),
            'pet_name': pet_name,
            'pet_type': pet_type,
            'title': title,
            'content': content,
            'media_url': media_url or 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80',
            'media_type': 'IMAGE',
            'score': 10, # 신규 등록 기본 점수
            'view_count': 1,
            'like_count': 1,
            'comment_count': 0,
            'share_count': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.posts[post_id] = new_post
        return new_post

# 싱글톤 서비스 객체 생성
service = PawStarService()
