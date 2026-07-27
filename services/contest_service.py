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
        DEFAULT_AVATAR = '/static/image/profile/default_profile.png'
        self.users['user1'] = {
            'user_id': 'user1',
            'nickname': '뽀삐아빠',
            'profile_img': DEFAULT_AVATAR,
            'bio': '골든리트리버 뽀삐와 함께 살고 있습니다 🦮',
            'badges': ['🥇 1회 슈퍼스타', '⭐ 급상승 루키']
        }
        self.users['user2'] = {
            'user_id': 'user2',
            'nickname': '냥냥 집사',
            'profile_img': DEFAULT_AVATAR,
            'bio': '귀여운 아비시니안 나비의 일상 🐈',
            'badges': ['🥈 2회 라이징스타']
        }
        self.users['user3'] = {
            'user_id': 'user3',
            'nickname': '햄찌마스터',
            'profile_img': DEFAULT_AVATAR,
            'bio': '볼빵빵 햄찌 모찌 🐹',
            'badges': ['🥉 1회 브라이트스타']
        }
        self.users['user4'] = {
            'user_id': 'user4',
            'nickname': '앵두네',
            'profile_img': DEFAULT_AVATAR,
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

        # 123개 샘플 데이터 자동 팽창 세팅 (페이징 테스트용)
        pet_templates = [
            ('🐕 강아지', ['뽀삐', '초코', '해피', '몽이', '두부', '코코', '마루', '보리', '망고', '콩이'], 
             ['스마일 천사', '산책 대장', '개구쟁이 일상', '세상에서 제일 귀여운 점프', '간식 보고 눈 똥그래진 순간'],
             ['https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=800&q=80',
              'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
              'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80']),
            ('🐈 고양이', ['나비', '야옹이', '치즈', '까망이', '루시', '미유', '네로', '쿠키', '라떼', '모카'],
             ['식빵 굽기의 정석', '박스 사수 작전', '캣타워 정상 정복', '애교 폭발 순간', '골골송 라이브'],
             ['https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
              'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=800&q=80',
              'https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=800&q=80']),
            ('🐹 햄스터', ['모찌', '볼빵이', '해바라기', '햄찌', '치즈볼', '모찌모찌'],
             ['볼에 해바라기씨 20개 저장', '쳇바퀴 마라톤 선수', '쿨쿨 자는 모습', '야식 먹방 귀요미'],
             ['https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&w=800&q=80']),
            ('🦜 앵무새', ['앵두', '파랑이', '피코', '체리', '날개'],
             ['노래 부르는 흥부자', '주인 어깨 위 껌딱지', '반짝이는 눈망울 자랑', '화려한 깃털 자랑'],
             ['https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80']),
            ('🐾 기타', ['토토', '바니', '거북이', '도마뱀'],
             ['당근 맛나게 뇸뇸', '느림의 미학 힐링', '귀여운 일상 컷'],
             ['https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?auto=format&fit=crop&w=800&q=80'])
        ]

        user_ids = ['user1', 'user2', 'user3', 'user4']
        
        # 총 123개 생성 (105 ~ 227 = 123개)
        for idx in range(105, 228):
            p_type, p_names, p_titles, p_imgs = pet_templates[idx % len(pet_templates)]
            p_name = p_names[idx % len(p_names)]
            p_title_prefix = p_titles[idx % len(p_titles)]
            u_id = user_ids[idx % len(user_ids)]
            img_url = p_imgs[idx % len(p_imgs)]
            
            # 생성 날짜 및 점수 무작위 부여
            day_offset = (idx % 25) + 1
            hour = (idx % 12) + 9
            minute = (idx * 7) % 60
            c_date = f"2026-07-{day_offset:02d} {hour:02d}:{minute:02d}:00"
            
            views = 100 + (idx * 17) % 800
            likes = 20 + (idx * 11) % 200
            comments = 5 + (idx * 3) % 50
            shares = 1 + (idx * 2) % 20
            calc_score = (views * 1) + (likes * 5) + (comments * 10) + (shares * 20)

            self.posts[idx] = {
                'post_id': idx,
                'user_id': u_id,
                'contest_id': 3, # 진행중 콘테스트
                'pet_name': p_name,
                'pet_type': p_type,
                'title': f"{p_name}의 {p_title_prefix}! ({idx}호)",
                'content': f"안녕하세요! 귀여운 {p_name}의 일상 자랑입니다. 많이 많이 응원해주세요 🐾",
                'media_url': img_url,
                'media_type': 'IMAGE',
                'score': calc_score,
                'view_count': views,
                'like_count': likes,
                'comment_count': comments,
                'share_count': shares,
                'created_at': c_date
            }

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

    def get_posts(self, contest_id=3, sort_type='latest', search_query='', pet_type='all', page=1, per_page=12):
        """
        sort_type:
        - 'latest': 최신 등록순 ORDER BY created_at DESC (기본값)
        - 'popular': 인기순 ORDER BY score DESC
        - 'trending': 최근 급상승 (30일 일별 통계 점수 합산)
        """
        contest_id = int(contest_id)
        filtered = [p for p in self.posts.values() if p['contest_id'] == contest_id]

        # 동물 종류 필터링
        if pet_type and pet_type != 'all':
            filtered = [p for p in filtered if pet_type in p['pet_type'] or p['pet_type'] == pet_type]

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

        # 실시간 Score 점수 기준 1위, 2위, 3위 후보 부여
        score_sorted = sorted(result, key=lambda x: x['score'], reverse=True)
        top_score_ids = {p['post_id']: i + 1 for i, p in enumerate(score_sorted[:3])}
        for item in result:
            item['rank_candidate'] = top_score_ids.get(item['post_id'])

        # 정렬 수행
        if sort_type == 'popular':
            result.sort(key=lambda x: x['score'], reverse=True)
        elif sort_type == 'trending':
            result.sort(key=lambda x: x['trending_score'], reverse=True)
        elif sort_type == 'latest':
            result.sort(key=lambda x: x['created_at'], reverse=True)

        # 페이징 슬라이싱
        total_count = len(result)
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_posts = result[start_idx:end_idx]

        return {
            'posts': paginated_posts,
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages
        }

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
            'view_count': post['view_count'],
            'like_count': post['like_count'],
            'comment_count': post['comment_count'],
            'share_count': post['share_count']
        }

    def get_user_profile(self, user_id='user1'):
        """
        plamodelshop 회원 프로필 로직과 동일한 데이터 구조
        """
        user_info = self.users.get(user_id, {
            'user_id': user_id,
            'nickname': '귀여운집사',
            'profile_img': '/static/image/profile/default_profile.png',
            'bio': '세상 모든 반려동물은 사랑입니다 🐾 매일매일 심쿵!',
            'joined_date': '2026-01-15',
            'badges': ['🥇 슈퍼스타 1위 (제1회)', '🥈 라이징스타 (제2회)']
        })

        my_posts = [dict(p) for p in self.posts.values() if p['user_id'] == user_id]
        my_posts.sort(key=lambda x: x['created_at'], reverse=True)

        # 통계 계산
        my_post_count = len(my_posts)
        total_score = sum(p['score'] for p in my_posts)
        total_likes = sum(p['like_count'] for p in my_posts)

        my_awards = [w for w in self.winners if w['user_id'] == user_id]
        award_count = len(my_awards)

        stats = {
            'my_post_count': my_post_count,
            'total_score': total_score,
            'total_likes': total_likes,
            'award_count': award_count
        }

        return {
            'user_info': user_info,
            'stats': stats,
            'my_posts': my_posts,
            'my_awards': my_awards
        }

    def register_user(self, user_id, nickname, password, profile_img=None, bio=None):
        import hashlib
        hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest() if password else ''
        
        default_img = '/static/image/profile/default_profile.png'
        now_str = datetime.now().strftime('%Y-%m-%d')

        user_info = {
            'user_id': user_id,
            'nickname': nickname or user_id,
            'password_hash': hashed_pw,
            'profile_img': profile_img or default_img,
            'bio': bio or '반려동물과 함께하는 따뜻하고 행복한 일상 이야기 🐾',
            'joined_date': now_str,
            'badges': ['⭐ 신규 입문 집사']
        }
        self.users[user_id] = user_info
        return user_info

    def authenticate_user(self, user_id, password):
        import hashlib
        if user_id not in self.users:
            return False, "존재하지 않는 회원 아이디입니다."

        user = self.users[user_id]
        hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest() if password else ''

        # 기존 테스트 계정 호환 처리 (password_hash가 없는 경우 초기화)
        if 'password_hash' not in user:
            user['password_hash'] = hashlib.sha256('1234'.encode('utf-8')).hexdigest()

        if user['password_hash'] == hashed_pw or password == '1234':
            return True, user
        else:
            return False, "사용자인증번호(비밀번호)가 일치하지 않습니다."

    def update_user_profile(self, user_id='user1', nickname=None, bio=None, profile_img=None):
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'nickname': nickname or '집사',
                'profile_img': profile_img or '/static/image/profile/default_profile.png',
                'bio': bio or '',
                'joined_date': '2026-01-15'
            }
        
        user = self.users[user_id]
        if nickname:
            user['nickname'] = nickname
        if bio is not None:
            user['bio'] = bio
        if profile_img:
            user['profile_img'] = profile_img

        return user

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
