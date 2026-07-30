import pymysql
import random
import hashlib
from datetime import datetime, timedelta
from config import db_config

def hash_id(raw_id):
    return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

def seed_database():
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()

    try:
        # 외래키 체크 비활성화 후 기존 데이터 정리
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = ["USER_BADGE", "BADGE", "CONTEST_WINNER", "POST_DAILY_STAT", "POST", "CONTEST", "USERS"]
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table};")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 1. Users (USER_ID를 복호화 불가능한 단방향 SHA-256 해시로 저장)
        DEFAULT_AVATAR = '/static/image/profile/default_profile.png'
        users_data = [
            (hash_id('user1'), '뽀삐아빠', DEFAULT_AVATAR, '골든리트리버 뽀삐와 함께 살고 있습니다 🦮', 'USER'),
            (hash_id('user2'), '냥냥 집사', DEFAULT_AVATAR, '귀여운 아비시니안 나비의 일상 🐈', 'USER'),
            (hash_id('user3'), '햄찌마스터', DEFAULT_AVATAR, '볼빵빵 햄찌 모찌 🐹', 'USER'),
            (hash_id('user4'), '앵두네', DEFAULT_AVATAR, '노래하는 모란앵무 앵두 🦜', 'USER')
        ]
        sql_user = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO, ROLE)
                      VALUES (%s, %s, %s, %s, %s)"""
        cur.executemany(sql_user, users_data)

        # 2. Contests (1월~12월 각 월별 테마 콘테스트명과 멘트)
        contests_data = [
            (1, '제1회 새해 맞이 펫스타 콘테스트', '새해 복 많이 받아라냥! 2026년 첫 번째 펫 슈퍼스타에 도전하세요 🌅🐾', '2026-01-01 00:00:00', '2026-01-31 23:59:59', 'CLOSED', ''),
            (2, '제2회 발렌타인 심쿵 콘테스트', '달콤함 폭발! 사르르 녹아내리는 우리 아이의 사랑스러운 심쿵 모먼트 🍫❤️', '2026-02-01 00:00:00', '2026-02-28 23:59:59', 'CLOSED', ''),
            (3, '제3회 봄맞이 설렘 펫 콘테스트', '살랑살랑 봄바람 타고 찾아온 미소 천사 펫 스타 🌸🐝', '2026-03-01 00:00:00', '2026-03-31 23:59:59', 'CLOSED', ''),
            (4, '제4회 벚꽃 피크닉 펫 챔피언십', '벚꽃 길 따라 화사하게 터지는 댕냥이들의 심쿵 피크닉 자랑 🌸🐕', '2026-04-01 00:00:00', '2026-04-30 23:59:59', 'CLOSED', ''),
            (5, '제5회 가정의 달 펫 패밀리 콘테스트', '우리 집 보물 1호! 세상에서 가장 따뜻한 반려동물 가족의 순간 🏡💖', '2026-05-01 00:00:00', '2026-05-31 23:59:59', 'CLOSED', ''),
            (6, '제6회 청량 힐링 펫 콘테스트', '초여름의 싱그러움 가득! 보는 것만으로 힐링되는 펫 스타 🌿🌊', '2026-06-01 00:00:00', '2026-06-30 23:59:59', 'CLOSED', ''),
            (7, '제7회 썸머 파라다이스 펫 콘테스트', '세상에서 가장 사랑스러운 우리 아이의 심쿵 모먼트! 무더위를 싹 씻어줄 시원하고 러블리한 펫 스타 🌊🍦', '2026-07-01 00:00:00', '2026-07-31 23:59:59', 'IN_PROGRESS', ''),
            (8, '제8회 한여름 밤의 바캉스 펫 챔피언십', '뜨거운 여름 열기보다 더 핫한 인플루언서 펫 축제 🏖️⭐', '2026-08-01 00:00:00', '2026-08-31 23:59:59', 'SCHEDULED', ''),
            (9, '제9회 가을 풍요 펫 콘테스트', '마음까지 넉넉해지는 풍성한 가을 둥글둥글 귀요미들 🍂🌾', '2026-09-01 00:00:00', '2026-09-30 23:59:59', 'SCHEDULED', ''),
            (10, '제10회 할로윈 펌킨 펫 스타전', '귀여운 유령 등장! 심장 멎는 큐트 할로윈 코스튬 파티 🎃👻', '2026-10-01 00:00:00', '2026-10-31 23:59:59', 'SCHEDULED', ''),
            (11, '제11회 단풍 낭만 펫 콘테스트', '바스락 단풍잎과 함께 찾아온 감성 만점 댕냥이 라이프 🍁☕', '2026-11-01 00:00:00', '2026-11-30 23:59:59', 'SCHEDULED', ''),
            (12, '제12회 홀리데이 크리스마스 펫 챔피언십', '메리 크리스마스! 산타 옷 입은 세상에서 가장 사랑스러운 선물 🎄🎁', '2026-12-01 00:00:00', '2026-12-31 23:59:59', 'SCHEDULED', '')
        ]
        sql_contest = """INSERT INTO CONTEST (CONTEST_ID, TITLE, DESCRIPTION, START_DATE, END_DATE, STATUS, BANNER_IMG)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_contest, contests_data)

        # 3. Sample Posts Generation using D:\dev\pawstar\sample_image (sample_01.jpg ~ sample_20.jpg)
        sample_images = [f"sample_{i:02d}.jpg" for i in range(1, 21)]
        
        pet_templates = [
            ('🐕 강아지', ['뽀삐', '초코', '해피', '몽이', '두부', '코코', '마루', '보리', '망고', '콩이'], 
             ['스마일 천사', '산책 대장', '개구쟁이 일상', '세상에서 제일 귀여운 점프', '간식 보고 눈 똥그래진 순간', '햇살 모닝 인사', '잔디밭 신나는 미소', '낮잠 부비부비']),
            ('🐈 고양이', ['나비', '야옹이', '치즈', '까망이', '루시', '미유', '네로', '쿠키', '라떼', '모카'],
             ['식빵 굽기의 정석', '박스 사수 작전', '캣타워 정상 정복', '애교 폭발 순간', '골골송 라이브', '햇살 캣닢 타임', '분홍 발바닥 젤리 자랑']),
            ('🐹 햄스터', ['모찌', '볼빵이', '해바라기', '햄찌', '치즈볼', '모찌모찌', '모찌군'],
             ['볼에 해바라기씨 20개 저장', '쳇바퀴 마라톤 선수', '쿨쿨 자는 모습', '야식 먹방 귀요미', '손바닥 위 오물오물']),
            ('🦜 앵무새', ['앵두', '파랑이', '피코', '체리', '날개', '피치'],
             ['노래 부르는 흥부자', '주인 어깨 위 껌딱지', '반짝이는 눈망울 자랑', '화려한 깃털 자랑', '헤드뱅잉 흥부자']),
            ('🐾 기타', ['토토', '바니', '거북이', '도마뱀', '포동이'],
             ['당근 맛나게 뇸뇸', '느림의 미학 힐링', '귀여운 일상 컷', '힐링 귀요미 순간'])
        ]

        user_ids = ['user1', 'user2', 'user3', 'user4']
        full_posts = []

        post_id_counter = 101

        # 1회~7회 콘테스트 포스트 생성 (각 회차당 20개씩)
        for contest_id_val in range(1, 8):
            for i in range(20):
                pid = post_id_counter
                post_id_counter += 1

                p_type, p_names, p_titles = pet_templates[(pid + i) % len(pet_templates)]
                p_name = p_names[(pid + i) % len(p_names)]
                p_title_prefix = p_titles[(pid + i) % len(p_titles)]
                u_id = user_ids[(pid + i) % len(user_ids)]
                
                img_name = sample_images[(pid - 101) % len(sample_images)]

                month_str = f"{contest_id_val:02d}"
                day_offset = (i % 25) + 1
                hour = (i % 12) + 9
                minute = (pid * 7) % 60
                c_date = f"2026-{month_str}-{day_offset:02d} {hour:02d}:{minute:02d}:00"

                views = 150 + (pid * 19) % 1200
                likes = 30 + (pid * 13) % 450
                comments = 8 + (pid * 5) % 90
                shares = 2 + (pid * 3) % 35
                calc_score = (views * 1) + (likes * 5) + (comments * 10) + (shares * 20)

                full_posts.append((
                    pid, hash_id(u_id), contest_id_val, p_name, p_type,
                    f"[{contest_id_val}회] {p_name}의 {p_title_prefix}!",
                    f"안녕하세요! {contest_id_val}회 Paw Star 콘테스트 참가작 {p_name}의 일상 자랑입니다 💕 예쁘게 봐주시고 응원 투표 부탁드려요 🐾",
                    '/static/sample_image/', img_name, img_name,
                    'IMAGE', calc_score, views, likes, comments, shares, c_date
                ))

        sql_post = """INSERT INTO POST (POST_ID, USER_ID, CONTEST_ID, PET_NAME, PET_TYPE, TITLE, CONTENT, FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, MEDIA_TYPE, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT, CREATED_AT)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_post, full_posts)

        # 4. Daily Stats
        today = datetime.now().date()
        daily_stats = []
        for post in full_posts:
            post_id = post[0]
            for i in range(15):
                stat_date = str(today - timedelta(days=i))
                v = random.randint(5, 30)
                l = random.randint(1, 10)
                c = random.randint(0, 4)
                s = random.randint(0, 2)
                daily_stats.append((post_id, stat_date, v, l, c, s))

        sql_stat = """INSERT INTO POST_DAILY_STAT (POST_ID, STAT_DATE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT)
                      VALUES (%s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_stat, daily_stats)

        # 5. Contest Winners (종료된 1회~6회 수상자 데이터)
        winners_data = []
        # 1회: post 101~120, 2회: 121~140, 3회: 141~160, 4회: 161~180, 5회: 181~200, 6회: 201~220
        for c_id in range(1, 7):
            base_p = 101 + (c_id - 1) * 20
            winners_data.extend([
                (c_id, base_p + 0, hash_id('user1'), 'SUPER_STAR', '🥇 Paw Star 골드 트로피'),
                (c_id, base_p + 1, hash_id('user2'), 'RISING_STAR', '🥈 Paw Star 실버 트로피'),
                (c_id, base_p + 2, hash_id('user3'), 'BRIGHT_STAR', '🥉 Paw Star 브론즈 트로피'),
                (c_id, base_p + 3, hash_id('user4'), 'ROOKIE_STAR', '⭐ 루키 스타 1위 특별상'),
                (c_id, base_p + 4, hash_id('user1'), 'ROOKIE_STAR', '⭐ 루키 스타 2위 특별상'),
                (c_id, base_p + 5, hash_id('user2'), 'ROOKIE_STAR', '⭐ 루키 스타 3위 특별상')
            ])
        sql_winner = """INSERT INTO CONTEST_WINNER (CONTEST_ID, POST_ID, USER_ID, AWARD_TYPE, PRIZE_NAME)
                        VALUES (%s, %s, %s, %s, %s)"""
        cur.executemany(sql_winner, winners_data)

        # 6. Badges & User Badges
        badges = [
            (1, '🥇 1회 슈퍼스타', 'trophy-gold', '제1회 콘테스트 1위 수상'),
            (2, '🥈 2회 라이징스타', 'trophy-silver', '제2회 콘테스트 2위 수상'),
            (3, '🥉 1회 브라이트스타', 'trophy-bronze', '제1회 콘테스트 3위 수상'),
            (4, '⭐ 루키스타', 'star-rookie', '급상승 1위 루키 수상')
        ]
        sql_badge = """INSERT INTO BADGE (BADGE_ID, BADGE_NAME, BADGE_ICON, DESCRIPTION) VALUES (%s, %s, %s, %s)"""
        cur.executemany(sql_badge, badges)

        user_badges = [
            (hash_id('user1'), 1),
            (hash_id('user2'), 2),
            (hash_id('user3'), 3),
            (hash_id('user4'), 4)
        ]
        sql_ubadge = """INSERT INTO USER_BADGE (USER_ID, BADGE_ID) VALUES (%s, %s)"""
        cur.executemany(sql_ubadge, user_badges)

        conn.commit()
        print("Successfully seeded all data into DB_PST!")

    except Exception as e:
        conn.rollback()
        print("Error seeding database:", e)
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
