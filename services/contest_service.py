"""
Paw Star Contest & Ranking Service
"""

from datetime import datetime, timedelta
import random
import pymysql
from config import db_config

class PawStarService:
    def __init__(self):
        self.contests = {}
        self.posts = {}
        self.daily_stats = [] # list of dicts
        self.winners = [] # list of dicts
        self.users = {}
        self.comments = [
            {'comment_id': 1, 'post_id': 1, 'user_nickname': '뽀삐집사_4955', 'user_profile': '/static/image/profile/default_profile.png', 'content': '세상에 너무 귀여워요! 심쿵 💖', 'created_at': '2026-07-29 10:15'},
            {'comment_id': 2, 'post_id': 1, 'user_nickname': '냥집사', 'user_profile': '/static/image/profile/default_profile.png', 'content': '1위 우승 예감이네요!! 🐾', 'created_at': '2026-07-29 11:30'},
            {'comment_id': 3, 'post_id': 2, 'user_nickname': '멍멍이파', 'user_profile': '/static/image/profile/default_profile.png', 'content': '눈빛이 너무 사랑스러워요 🌟', 'created_at': '2026-07-29 14:20'},
            {'comment_id': 4, 'post_id': 3, 'user_nickname': '귀요미덕후', 'user_profile': '/static/image/profile/default_profile.png', 'content': '무조건 10점 득점 응원합니다!', 'created_at': '2026-07-29 15:45'},
        ]
        
        # 데이터베이스(DB_PST)에서 데이터 불러오기 시도
        if not self.load_data_from_db():
            self._init_mock_data()

    def get_db_connection(self):
        try:
            return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            print("DB Connection Error:", e)
            return None

    def load_data_from_db(self):
        """ DB_PST 데이터베이스의 테이블에서 직접 데이터를 인출하여 서비스 스토어 구성 """
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # 0. POST 테이블 컬럼 자동 마이그레이션 (MEDIA_URL -> IMAGE_PATH)
                try:
                    cur.execute("SHOW COLUMNS FROM POST LIKE 'MEDIA_URL'")
                    if cur.fetchone():
                        cur.execute("ALTER TABLE POST CHANGE MEDIA_URL IMAGE_PATH VARCHAR(255) NOT NULL")
                        conn.commit()
                        print("DB DDL 실행 성공: POST 테이블 MEDIA_URL -> IMAGE_PATH 컬럼명 변경 완료")
                except Exception as ex:
                    print("DB DDL 마이그레이션 예외 통과:", ex)

                # 1. USERS 테이블 데이터 가져오기
                cur.execute("SELECT * FROM USERS")
                db_users = cur.fetchall()
                if db_users:
                    self.users = {}
                    for u in db_users:
                        # 사용자별 배지 목록 가져오기
                        cur.execute("""
                            SELECT b.BADGE_NAME 
                            FROM USER_BADGE ub 
                            JOIN BADGE b ON ub.BADGE_ID = b.BADGE_ID 
                            WHERE ub.USER_ID = %s
                        """, (u['USER_ID'],))
                        badge_rows = cur.fetchall()
                        badges = [b['BADGE_NAME'] for b in badge_rows]

                        self.users[u['USER_ID']] = {
                            'user_id': u['USER_ID'],
                            'nickname': u['NICKNAME'],
                            'profile_img': u['PROFILE_IMG'],
                            'bio': u['BIO'] or '',
                            'badges': badges
                        }

                # 2. CONTEST 테이블 데이터 가져오기
                cur.execute("SELECT * FROM CONTEST")
                db_contests = cur.fetchall()
                if db_contests:
                    self.contests = {}
                    for c in db_contests:
                        start_str = c['START_DATE'].strftime('%Y-%m-%d') if isinstance(c['START_DATE'], datetime) else str(c['START_DATE'])[:10]
                        end_str = c['END_DATE'].strftime('%Y-%m-%d') if isinstance(c['END_DATE'], datetime) else str(c['END_DATE'])[:10]
                        status_kr = '진행중' if c['STATUS'] == 'IN_PROGRESS' else ('종료' if c['STATUS'] == 'CLOSED' else '예정')
                        
                        self.contests[c['CONTEST_ID']] = {
                            'contest_id': c['CONTEST_ID'],
                            'title': c['TITLE'],
                            'start_date': start_str,
                            'end_date': end_str,
                            'status': status_kr,
                            'description': c['DESCRIPTION'] or ''
                        }

                # 3. POST 테이블 데이터 가져오기
                cur.execute("SELECT * FROM POST")
                db_posts = cur.fetchall()
                if db_posts:
                    self.posts = {}
                    for p in db_posts:
                        created_str = p['CREATED_AT'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(p['CREATED_AT'], datetime) else str(p['CREATED_AT'])
                        self.posts[p['POST_ID']] = {
                            'post_id': p['POST_ID'],
                            'user_id': p['USER_ID'],
                            'contest_id': p['CONTEST_ID'],
                            'pet_name': p['PET_NAME'],
                            'pet_type': p['PET_TYPE'],
                            'title': p['TITLE'],
                            'content': p['CONTENT'] or '',
                            'file_path': p.get('FILE_PATH') or '/static/image/paw/2026/07/',
                            'list_file_name': p.get('LIST_FILE_NAME') or f"3-{p['POST_ID']}_list.webp",
                            'popup_file_name': p.get('POPUP_FILE_NAME') or f"3-{p['POST_ID']}_popup.webp",
                            'media_type': p['MEDIA_TYPE'],
                            'score': p['SCORE'],
                            'view_count': p['VIEW_COUNT'],
                            'like_count': p['LIKE_COUNT'],
                            'comment_count': p['COMMENT_COUNT'],
                            'share_count': p['SHARE_COUNT'],
                            'created_at': created_str
                        }

                # 4. POST_DAILY_STAT 테이블 데이터 가져오기
                cur.execute("SELECT * FROM POST_DAILY_STAT")
                db_stats = cur.fetchall()
                if db_stats:
                    self.daily_stats = []
                    for s in db_stats:
                        stat_date_str = str(s['STAT_DATE'])
                        self.daily_stats.append({
                            'post_id': s['POST_ID'],
                            'stat_date': stat_date_str,
                            'view_count': s['VIEW_COUNT'],
                            'like_count': s['LIKE_COUNT'],
                            'comment_count': s['COMMENT_COUNT'],
                            'share_count': s['SHARE_COUNT']
                        })

                # 5. CONTEST_WINNER 테이블 데이터 가져오기
                cur.execute("""
                    SELECT w.*, c.TITLE as CONTEST_TITLE, p.PET_NAME, p.PET_TYPE, p.TITLE as POST_TITLE, 
                           p.*, u.NICKNAME as USER_NICKNAME, u.PROFILE_IMG as USER_PROFILE
                    FROM CONTEST_WINNER w
                    JOIN CONTEST c ON w.CONTEST_ID = c.CONTEST_ID
                    JOIN POST p ON w.POST_ID = p.POST_ID
                    JOIN USERS u ON w.USER_ID = u.USER_ID
                """)
                db_winners = cur.fetchall()
                if db_winners:
                    self.winners = []
                    for w in db_winners:
                        self.winners.append({
                            'contest_id': w['CONTEST_ID'],
                            'post_id': w['POST_ID'],
                            'user_id': w['USER_ID'],
                            'award_type': w['AWARD_TYPE'],
                            'prize_name': w['PRIZE_NAME'],
                            'pet_name': w['PET_NAME'],
                            'pet_type': w['PET_TYPE'],
                            'post_title': w['POST_TITLE'],
                            'file_path': w.get('FILE_PATH') or '/static/image/paw/2026/07/',
                            'list_file_name': w.get('LIST_FILE_NAME') or f"3-{w['POST_ID']}_list.webp",
                            'popup_file_name': w.get('POPUP_FILE_NAME') or f"3-{w['POST_ID']}_popup.webp",
                            'score': w['SCORE'],
                            'user_nickname': w['USER_NICKNAME'],
                            'user_profile': w['USER_PROFILE']
                        })

            print("Successfully loaded all data from DB_PST tables!")
            return True
        except Exception as e:
            print("Error loading data from DB_PST:", e)
            return False
        finally:
            conn.close()

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
        # 유저별 좋아요 누른 게시물 ID 집합 (user_id -> set of post_ids)
        self.user_likes = {}
        # 유저별 이미 조회를 완료한 게시물 ID 집합 (user_id -> set of post_ids)
        self.user_views = {}
        # 유저별 댓글을 작성한 게시물 ID 집합
        self.user_comments = {}
        # 유저별 공유를 수행한 게시물 ID 집합
        self.user_shares = {}

        # Posts for Contest #3 (진행중) 20개 샘플 데이터
        sample_posts = []
        pet_meta_list = [
            ("뽀삐", "🐕 강아지", "웃는 모습이 너무 예쁜 우리 뽀삐 자랑해요!", "오늘 잔디밭 산책 다녀왔는데 기분이 너무 좋은지 햇살 아래서 천사처럼 웃네요 💕"),
            ("나비", "🐈 고양이", "박스만 보면 일단 들어가고 보는 나비의 하루", "택배 박스 뜯자마자 식빵 굽기 완성! 이 굴뚝같은 귀여움 어쩌죠? 🐾"),
            ("모찌", "🐹 햄스터", "볼따구에 해바라기씨 10개 저장 성공!", "볼이 터질 것 같은 볼빵빵 모찌입니다. 귀여운 먹방 구경오세요~"),
            ("앵두", "🦜 앵무새", "주인 껌딱지 앵두의 헤드뱅잉 장기자랑", "신나는 음악 틀어주면 박자에 맞춰서 날개를 흔드는 흥부자 앵두랍니다 🎶"),
            ("초코", "🐕 강아지", "초코송이 귀를 가진 심쿵 푸들 초코", "복슬복슬 귀여운 초코! 털 깎고 더욱 귀여워졌어요~"),
            ("라떼", "🐈 고양이", "라떼처럼 부드러운 털을 가진 오드아이 냥이", "눈동자 색깔이 오드아이로 매력 넘치는 고양이 라떼의 매력에 빠져보세요."),
            ("해피", "🐕 강아지", "산책 가자는 말에 미소 짓는 해피", "산책 소리만 들으면 신나서 빙글빙글 도는 똥꼬발랄 해피입니다!"),
            ("구름", "🐕 강아지", "하늘에서 내려온 솜사탕 구름이", "뽀송뽀송 뭉게구름 같은 우리 강아지 솜사탕처럼 달콤하죠?"),
            ("망고", "🐈 고양이", "노랑노랑 망고의 따사로운 햇살 식빵", "창가 햇살 아래에서 졸고 있는 노란 애교쟁이 망고 자랑합니다."),
            ("두부", "🐕 강아지", "말랑말랑 순두부 같은 미소 두부", "이름처럼 말랑하고 성격도 온순한 두부의 힐링 사진입니다."),
            ("까미", "🐈 고양이", "검은 고양이 까미의 귀여운 젤리 공개", "분홍빛 젤리 발바닥이 매력 포인트! 귀여운 까미 자랑해요."),
            ("보리", "🐕 강아지", "보리밭 산책왕 보리의 가을 나들이", "바람을 느끼는 멋진 가을 남자 보리의 산책 포즈!"),
            ("콩이", "🐹 햄스터", "손바닥에 쏙 들어오는 귀요미 콩이", "작고 소중한 콩이의 앙증맞은 손 귀여움 폭발입니다."),
            ("피코", "🦜 앵무새", "알록달록 예쁜 깃털 뽐내는 피코", "화려한 깃털 옷을 입고 인사하는 안녕 피코랍니다."),
            ("마루", "🐕 강아지", "쇼파를 장악한 강아지 마루의 휴식", "사람처럼 쇼파에 기대어 TV 보는 귀여운 마루의 하루"),
            ("코코", "🐈 고양이", "높은 곳을 좋아하는 탐험가 코코", "캣타워 최상층에서 아래를 내려다보는 멋진 코코의 모습"),
            ("치즈", "🐈 고양이", "노란 치즈냥이의 골골송 라이브", "쓰다듬어주면 골골송을 부르는 최고 귀요미 치즈랍니다."),
            ("단풍", "🐕 강아지", "단풍잎 밟으며 신난 가을 강아지", "낙엽 밟는 소리가 좋은지 뛰어다니는 단풍이 자랑해요!"),
            ("모카", "🐕 강아지", "초롱초롱 인형 같은 눈망울 모카", "까만 콩 세 개 찍힌 것처럼 인형 같은 모카 사진 보세요."),
            ("하늘", "🦜 앵무새", "파란 하늘 닮은 깃털 파랑이 하늘이", "청량한 파란색 깃털을 가진 사랑스러운 하늘이의 미소입니다.")
        ]

        for i in range(1, 21):
            pid = 100 + i
            meta = pet_meta_list[i-1]
            sample_posts.append({
                'post_id': pid,
                'user_id': f"user{(i % 6) + 1}",
                'contest_id': 3,
                'pet_name': meta[0],
                'pet_type': meta[1],
                'title': meta[2],
                'content': meta[3],
                'file_path': '/static/image/paw/2026/07/',
                'list_file_name': f"3-{pid}_list.webp",
                'popup_file_name': f"3-{pid}_popup.webp",
                'media_type': 'IMAGE',
                'score': 1000 + (20 - i) * 75,
                'view_count': 200 + (20 - i) * 25,
                'like_count': 60 + (20 - i) * 6,
                'comment_count': 15 + (20 - i) * 2,
                'share_count': 5 + (20 - i),
                'created_at': '2026-07-28 12:00:00'
            })

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
                'image_path': img_url,
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
            'image_path': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
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
            'image_path': 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
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
            'image_path': 'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&w=800&q=80',
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
            'image_path': 'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80',
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
        # 언제나 실제 MySQL DB에서 최신 데이터 동기화 읽기
        self.load_data_from_db()

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

            # 4가지 영향력 반영 상태 (조회, 좋아요, 댓글, 공유)
            item['actions'] = self.get_user_post_actions(p['post_id'], 'user1')

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

    def trigger_event(self, post_id, event_type, user_id=None):
        """
        이벤트 발생시 실시간 score 증가 (본인 게시물 점수 반영 차단)
        """
        post_id = int(post_id)
        if post_id not in self.posts:
            return None

        post = self.posts[post_id]

        # 본인 게시물 이벤트 수치/점수 반영 차단
        if user_id and post.get('user_id') == user_id:
            return {
                'success': False,
                'is_owner': True,
                'message': '본인의 게시물에는 점수 및 카운팅이 반영되지 않습니다.',
                'post_id': post_id,
                'new_score': post['score'],
                'view_count': post['view_count'],
                'like_count': post['like_count'],
                'comment_count': post['comment_count'],
                'share_count': post['share_count']
            }

        today_str = str(datetime.now().date())

        v_delta, l_delta, c_delta, s_delta = 0, 0, 0, 0
        if event_type == 'view':
            # 유저별 중복 조회 방지 검사
            if user_id:
                if not hasattr(self, 'user_views') or self.user_views is None:
                    self.user_views = {}
                if user_id not in self.user_views:
                    self.user_views[user_id] = set()
                
                # 이미 본 게시물인 경우 조회수/점수 증가 차단
                if post_id in self.user_views[user_id]:
                    return {
                        'success': False,
                        'already_viewed': True,
                        'message': '이미 조회가 완료된 게시물입니다.',
                        'post_id': post_id,
                        'new_score': post['score'],
                        'view_count': post['view_count'],
                        'like_count': post['like_count'],
                        'comment_count': post['comment_count'],
                        'share_count': post['share_count']
                    }
                self.user_views[user_id].add(post_id)

            v_delta = 1
            post['view_count'] += 1
        elif event_type == 'like':
            l_delta = 1
            post['like_count'] += 1
            if user_id:
                if not hasattr(self, 'user_likes') or self.user_likes is None:
                    self.user_likes = {}
                if user_id not in self.user_likes:
                    self.user_likes[user_id] = set()
                self.user_likes[user_id].add(post_id)
        elif event_type == 'unlike':
            l_delta = -1
            post['like_count'] = max(0, post['like_count'] - 1)
            if user_id:
                if not hasattr(self, 'user_likes') or self.user_likes is None:
                    self.user_likes = {}
                if user_id in self.user_likes:
                    self.user_likes[user_id].discard(post_id)
        elif event_type == 'comment':
            c_delta = 1
            post['comment_count'] += 1
            if user_id:
                if not hasattr(self, 'user_comments') or self.user_comments is None:
                    self.user_comments = {}
                if user_id not in self.user_comments:
                    self.user_comments[user_id] = set()
                self.user_comments[user_id].add(post_id)
        elif event_type == 'share':
            s_delta = 1
            post['share_count'] += 1
            if user_id:
                if not hasattr(self, 'user_shares') or self.user_shares is None:
                    self.user_shares = {}
                if user_id not in self.user_shares:
                    self.user_shares[user_id] = set()
                self.user_shares[user_id].add(post_id)

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

        # 실제 DB POST 테이블 및 POST_DAILY_STAT 에 수치 갱신 반영
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE POST 
                        SET SCORE = %s, VIEW_COUNT = %s, LIKE_COUNT = %s, COMMENT_COUNT = %s, SHARE_COUNT = %s 
                        WHERE POST_ID = %s
                    """, (post['score'], post['view_count'], post['like_count'], post['comment_count'], post['share_count'], post_id))

                    cur.execute("""
                        INSERT INTO POST_DAILY_STAT (POST_ID, STAT_DATE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            VIEW_COUNT = VIEW_COUNT + VALUES(VIEW_COUNT),
                            LIKE_COUNT = LIKE_COUNT + VALUES(LIKE_COUNT),
                            COMMENT_COUNT = COMMENT_COUNT + VALUES(COMMENT_COUNT),
                            SHARE_COUNT = SHARE_COUNT + VALUES(SHARE_COUNT)
                    """, (post_id, today_str, max(0, v_delta), max(0, l_delta), max(0, c_delta), max(0, s_delta)))
                    conn.commit()
                conn.close()
            except Exception as ex:
                print("이벤트 DB 동기화 오류:", ex)

        return {
            'post_id': post_id,
            'new_score': post['score'],
            'view_count': post['view_count'],
            'like_count': post['like_count'],
            'comment_count': post['comment_count'],
            'share_count': post['share_count']
        }

    def get_user_post_actions(self, post_id, user_id=None):
        """ 특정 유저가 특정 게시물에 반영한 4가지 영향력 상태 (조회, 좋아요, 댓글, 공유) 반환 """
        try:
            pid = int(post_id)
        except Exception:
            pid = post_id
        
        if not user_id:
            user_id = 'user1'

        is_viewed = False
        if hasattr(self, 'user_views') and user_id in self.user_views:
            is_viewed = (pid in self.user_views[user_id]) or (str(pid) in self.user_views[user_id])

        is_liked = False
        if hasattr(self, 'user_likes') and user_id in self.user_likes:
            is_liked = (pid in self.user_likes[user_id]) or (str(pid) in self.user_likes[user_id])

        is_commented = False
        user_nick = self.users.get(user_id, {}).get('nickname') if hasattr(self, 'users') else None
        if any(c.get('post_id') == pid and (c.get('user_id') == user_id or (user_nick and c.get('user_nickname') == user_nick)) for c in getattr(self, 'comments', [])):
            is_commented = True
        elif hasattr(self, 'user_comments') and user_id in self.user_comments:
            is_commented = (pid in self.user_comments[user_id]) or (str(pid) in self.user_comments[user_id])

        is_shared = False
        if hasattr(self, 'user_shares') and user_id in self.user_shares:
            is_shared = (pid in self.user_shares[user_id]) or (str(pid) in self.user_shares[user_id])

        return {
            'is_viewed': is_viewed,
            'is_liked': is_liked,
            'is_commented': is_commented,
            'is_shared': is_shared
        }

    def is_user_liked(self, post_id, user_id):
        """ 특정 유저가 게시물에 좋아요를 눌렀는지 여부 반환 """
        try:
            if not hasattr(self, 'user_likes') or self.user_likes is None:
                self.user_likes = {}
            if not user_id or user_id not in self.user_likes:
                return False
            liked_posts = self.user_likes.get(user_id, set())
            return (int(post_id) in liked_posts) or (str(post_id) in liked_posts)
        except Exception:
            return False

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

    def register_user(self, user_id, nickname, password=None, profile_img=None, bio=None):
        default_img = '/static/image/profile/default_profile.png'
        now_str = datetime.now().strftime('%Y-%m-%d')
        profile_img_path = profile_img or default_img
        user_bio = bio or '반려동물과 함께하는 따뜻하고 행복한 일상 이야기 🐾'

        user_info = {
            'user_id': user_id,
            'nickname': nickname or user_id,
            'profile_img': profile_img_path,
            'bio': user_bio,
            'joined_date': now_str,
            'badges': ['⭐ 신규 입문 집사']
        }
        self.users[user_id] = user_info

        # DB_PST의 USERS 테이블에 레코드 저장 (PASSWORD 칼럼 제외)
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    sql = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO)
                             VALUES (%s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE NICKNAME=%s, PROFILE_IMG=%s, BIO=%s"""
                    cur.execute(sql, (user_id, nickname or user_id, profile_img_path, user_bio, nickname or user_id, profile_img_path, user_bio))
                conn.commit()
            except Exception as e:
                print("DB insert user error:", e)
            finally:
                conn.close()

        return user_info

    def authenticate_user(self, user_id, password=None):
        if user_id not in self.users:
            return False, "존재하지 않는 회원 아이디입니다."
        user = self.users[user_id]
        return True, user

    def hash_user_id(self, raw_id):
        if not raw_id:
            return ""
        if len(str(raw_id)) == 64 and all(c in '0123456789abcdefABCDEF' for c in str(raw_id)):
            return str(raw_id).lower()
        import hashlib
        return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

    def google_login_or_register(self, google_id, email=None, default_name=None, picture=None):
        """ 구글 계정으로 로그인 또는 회원가입 (USER_ID는 단방향 SHA-256 해시로 안전 저장, 프로필 이미지는 구글 URL 그대로 적용) """
        raw_user_id = f"google_{google_id}"
        user_id = self.hash_user_id(raw_user_id)
        
        # 구글에서 넘겨받은 프로필 이미지 URL 그대로 사용
        profile_img = picture if (picture and picture.strip()) else '/static/image/profile/default_profile.png'

        if user_id not in self.users:
            import random
            now_str = datetime.now().strftime('%Y-%m-%d')
            
            prefix_list = [
                '귀여운집사', '행복집사', '초보집사', '댕냥집사', '심쿵집사',
                '멍냥이', '뽀삐집사', '나비집사', '사랑집사', '신난집사',
                '빛나는집사', '멋진집사', '포근집사', '큐트집사', '러블리집사'
            ]
            prefix = random.choice(prefix_list)
            rand_num = random.randint(1000, 9999)
            random_nickname = f"{prefix}_{rand_num}"

            user_info = {
                'user_id': user_id,
                'nickname': random_nickname,
                'profile_img': profile_img,
                'bio': 'PawStar에서 반려동물과 행복한 일상을 나누고 있습니다 🐾',
                'joined_date': now_str,
                'badges': ['🌐 Google 인증 회원']
            }
            self.users[user_id] = user_info

            # DB_PST USERS 테이블에 구글 프로필 이미지 URL 그대로 저장
            conn = self.get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        sql = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO, ROLE)
                                 VALUES (%s, %s, %s, %s, %s)
                                 ON DUPLICATE KEY UPDATE NICKNAME=%s, PROFILE_IMG=%s, BIO=%s"""
                        cur.execute(sql, (
                            user_id, random_nickname, profile_img, user_info['bio'], 'USER',
                            random_nickname, profile_img, user_info['bio']
                        ))
                    conn.commit()
                except Exception as e:
                    print("Error saving google user to DB:", e)
                finally:
                    conn.close()
        else:
            user_info = self.users[user_id]
            # 재로그인 시에도 구글 프로필 이미지 URL 반영
            if picture and picture.strip():
                user_info['profile_img'] = picture

            conn = self.get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        sql = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO, ROLE)
                                 VALUES (%s, %s, %s, %s, %s)
                                 ON DUPLICATE KEY UPDATE PROFILE_IMG=%s"""
                        cur.execute(sql, (
                            user_id, user_info['nickname'], user_info['profile_img'], user_info.get('bio', ''), 'USER',
                            user_info['profile_img']
                        ))
                    conn.commit()
                except Exception as e:
                    print("Error updating google user in DB:", e)
                finally:
                    conn.close()
        
        return self.users[user_id]

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

        # DB_PST USERS 테이블 업데이트
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    sql = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO)
                             VALUES (%s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE NICKNAME=%s, PROFILE_IMG=%s, BIO=%s"""
                    cur.execute(sql, (user_id, user['nickname'], user['profile_img'], user['bio'], user['nickname'], user['profile_img'], user['bio']))
                conn.commit()
            except Exception as e:
                print("Error updating user profile in DB:", e)
            finally:
                conn.close()

        return user

    def delete_user(self, user_id):
        """ 회원 탈퇴 처리: 사용자 계정 정보 및 관련 데이터 삭제 """
        if user_id in self.users:
            del self.users[user_id]

        # 해당 회원의 메모리 게시물 삭제
        posts_to_delete = [p_id for p_id, p in self.posts.items() if p.get('user_id') == user_id]
        for p_id in posts_to_delete:
            del self.posts[p_id]

        # 해당 회원의 메모리 수상 내역 삭제
        self.winners = [w for w in self.winners if w.get('user_id') != user_id]

        # DB_PST 데이터베이스에서 해당 회원 정보 및 연관 데이터(게시물, 배지 등 CASCADE) 삭제
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM USERS WHERE USER_ID = %s", (user_id,))
                conn.commit()
                print(f"Successfully deleted user '{user_id}' from DB_PST USERS table!")
            except Exception as e:
                print(f"Error deleting user '{user_id}' from DB:", e)
            finally:
                conn.close()

        return True

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
                'image_path': p.get('image_path') or p.get('media_url'),
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
                'image_path': p.get('image_path') or p.get('media_url'),
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
                'image_path': p.get('image_path') or p.get('media_url'),
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
                'image_path': rookie_post.get('image_path') or rookie_post.get('media_url'),
                'score': rookie_post['score'],
                'user_nickname': u.get('nickname', ''),
                'user_profile': u.get('profile_img', '')
            }
            new_winners.append(rookie_winner)
            self.winners.append(rookie_winner)

        return new_winners

    def get_next_post_id(self):
        """ 다음에 발급될 고유 post_id 반환 """
        return max(self.posts.keys(), default=100) + 1

    def create_post(self, contest_id, user_id, pet_name, pet_type, title, content, file_path, list_file_name, popup_file_name, force_post_id=None):
        post_id = int(force_post_id) if force_post_id else self.get_next_post_id()
        created_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 100% 실제 MySQL DB POST 테이블에 INSERT 영구 저장
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    # 유저 존재 여부 확인 및 자동 생성 (FK Constraint 충돌 방지)
                    cur.execute("SELECT USER_ID FROM USERS WHERE USER_ID = %s", (user_id,))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG) VALUES (%s, %s, %s)",
                                    (user_id, '회원 집사', '/static/image/profile/default_profile.png'))

                    sql = """INSERT INTO POST (POST_ID, USER_ID, CONTEST_ID, PET_NAME, PET_TYPE, TITLE, CONTENT, FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, MEDIA_TYPE, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT, CREATED_AT)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cur.execute(sql, (
                        post_id, user_id, int(contest_id), pet_name, pet_type, title, content,
                        file_path, list_file_name, popup_file_name, 'IMAGE',
                        0, 0, 0, 0, 0, created_at_str
                    ))
                    conn.commit()
                    print(f"MySQL DB POST 테이블 신규 레코드 #{post_id} 영구 저장 성공!")
                conn.close()
            except Exception as e:
                print("MySQL DB POST 저장 중 오류:", e)

        # DB 저장 직후 DB에서 최신 데이터 전체 재인출 및 동기화
        self.load_data_from_db()
        return self.posts.get(post_id)

    def get_comments_by_post(self, post_id):
        """ 특정 게시물의 댓글 목록 반환 및 실제 개수로 comment_count 동기화 """
        try:
            p_id = int(post_id)
        except (ValueError, TypeError):
            p_id = 1
        comments = [c for c in self.comments if c.get('post_id') == p_id]
        if p_id in self.posts:
            self.posts[p_id]['comment_count'] = len(comments)
        return comments

    def has_user_commented(self, post_id, user_id=None, user_nickname=None):
        """ 동일 게시물에 회원이 이미 댓글을 작성했는지 확인 """
        try:
            p_id = int(post_id)
        except (ValueError, TypeError):
            p_id = 1
        
        for c in self.comments:
            if c.get('post_id') == p_id:
                if user_id and c.get('user_id') == user_id:
                    return True
                if user_nickname and c.get('user_nickname') == user_nickname:
                    return True
        return False

    def add_comment(self, post_id, user_nickname, content, user_profile=None, user_id=None):
        """ 한줄 댓글 추가 및 10점 점수/댓글수 카운트 반영 (동일 타겟당 1회 제한 / 본인 게시물 불가) """
        try:
            p_id = int(post_id)
        except (ValueError, TypeError):
            p_id = 1

        # 1. 본인 게시물 댓글 작성 방지 체크
        post = self.posts.get(p_id)
        if post:
            post_author_id = post.get('user_id')
            post_author_nickname = post.get('user_nickname')
            if (user_id and post_author_id and user_id == post_author_id) or \
               (user_nickname and post_author_nickname and user_nickname == post_author_nickname):
                return None, "본인이 작성한 게시물에는 한줄 댓글을 작성할 수 없습니다."

        # 2. 동일 게시물 중복 작성 체크
        if self.has_user_commented(p_id, user_id=user_id, user_nickname=user_nickname):
            return None, "이미 이 게시물에 한줄 댓글을 작성하셨습니다. (1회 작성 가능)"

        new_comment_id = len(self.comments) + 1
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        comment = {
            'comment_id': new_comment_id,
            'post_id': p_id,
            'user_id': user_id or '',
            'user_nickname': user_nickname or '익명 집사',
            'user_profile': user_profile or '/static/image/profile/default_profile.png',
            'content': content,
            'created_at': now_str
        }
        self.comments.append(comment)
        # 댓글 이벤트 기록 (+10점 반영)
        event_res = self.trigger_event(p_id, 'comment')
        
        # 실제 등록된 댓글 개수로 정확히 카운트 동기화
        post_comments = [c for c in self.comments if c.get('post_id') == p_id]
        actual_count = len(post_comments)
        if p_id in self.posts:
            self.posts[p_id]['comment_count'] = actual_count
        if event_res:
            event_res['comment_count'] = actual_count
            
        return comment, event_res

# 싱글톤 서비스 객체 생성
service = PawStarService()
