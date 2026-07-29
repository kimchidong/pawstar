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

        # 2. Contests
        contests_data = [
            (1, '제1회 Paw Star 콘테스트', 'Paw Star 대망의 개막 1회 콘테스트 🎉', '2026-05-01 00:00:00', '2026-05-31 23:59:59', 'CLOSED', ''),
            (2, '제2회 Paw Star 콘테스트', '매일이 매력 폭발! 최고의 펫 스타를 가리는 콘테스트 🌟', '2026-06-01 00:00:00', '2026-06-30 23:59:59', 'CLOSED', ''),
            (3, '제3회 Paw Star 콘테스트', '세상에서 가장 사랑스러운 우리 아이의 심쿵 모먼트! 🌟 대한민국 대표 펫 스타에 도전하세요!', '2026-07-01 00:00:00', '2026-07-31 23:59:59', 'IN_PROGRESS', '')
        ]
        sql_contest = """INSERT INTO CONTEST (CONTEST_ID, TITLE, DESCRIPTION, START_DATE, END_DATE, STATUS, BANNER_IMG)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_contest, contests_data)

        # 3. Initial Posts (101~104)
        sample_posts = [
            (101, hash_id('user1'), 3, '뽀삐', '🐕 강아지', '웃는 모습이 너무 예쁜 우리 뽀삐 자랑해요!',
             '오늘 잔디밭 산책 다녀왔는데 기분이 너무 좋은지 햇살 아래서 천사처럼 웃네요 💕 다들 뽀삐 웃음 보고 힐링하세요!',
             'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=800&q=80', 'IMAGE', 1580, 320, 112, 40, 15, '2026-07-10 14:20:00'),
            (102, hash_id('user2'), 3, '나비', '🐈 고양이', '박스만 보면 일단 들어가고 보는 나비의 하루',
             '택배 박스 뜯자마자 식빵 굽기 완성! 이 굴뚝같은 귀여움 어쩌죠? 🐾',
             'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80', 'IMAGE', 1420, 410, 90, 32, 12, '2026-07-12 10:15:00'),
            (103, hash_id('user3'), 3, '모찌', '🐹 햄스터', '볼따구에 해바라기씨 10개 저장 성공!',
             '볼이 터질 것 같은 볼빵빵 모찌입니다. 귀여운 먹방 구경오세요~',
             'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&w=800&q=80', 'IMAGE', 1890, 590, 130, 45, 10, '2026-07-15 18:30:00'),
            (104, hash_id('user4'), 3, '앵두', '🦜 앵무새', '주인 껌딱지 앵두의 헤드뱅잉 장기자랑',
             '신나는 음악 틀어주면 박자에 맞춰서 날개를 흔드는 흥부자 앵두랍니다 🎶',
             'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80', 'IMAGE', 1210, 260, 80, 25, 15, '2026-07-18 09:00:00')
        ]

        # 105 ~ 227 posts
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
        all_posts = list(sample_posts)

        for idx in range(105, 228):
            p_type, p_names, p_titles, p_imgs = pet_templates[idx % len(pet_templates)]
            p_name = p_names[idx % len(p_names)]
            p_title_prefix = p_titles[idx % len(p_titles)]
            u_id = user_ids[idx % len(user_ids)]
            img_url = p_imgs[idx % len(p_imgs)]
            
            day_offset = (idx % 25) + 1
            hour = (idx % 12) + 9
            minute = (idx * 7) % 60
            c_date = f"2026-07-{day_offset:02d} {hour:02d}:{minute:02d}:00"
            
            views = 100 + (idx * 17) % 800
            likes = 20 + (idx * 11) % 200
            comments = 5 + (idx * 3) % 50
            shares = 1 + (idx * 2) % 20
            calc_score = (views * 1) + (likes * 5) + (comments * 10) + (shares * 20)

            all_posts.append((
                idx, hash_id(u_id), 3, p_name, p_type,
                f"{p_name}의 {p_title_prefix}! ({idx}호)",
                f"안녕하세요! 귀여운 {p_name}의 일상 자랑입니다. 많이 많이 응원해주세요 🐾",
                img_url, 'IMAGE', calc_score, views, likes, comments, shares, c_date
            ))

        sql_post = """INSERT INTO POST (POST_ID, USER_ID, CONTEST_ID, PET_NAME, PET_TYPE, TITLE, CONTENT, FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, MEDIA_TYPE, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT, CREATED_AT)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_post, all_posts)

        # 4. Daily Stats
        today = datetime.now().date()
        daily_stats = []
        for post in all_posts:
            post_id = post[0]
            for i in range(30):
                stat_date = str(today - timedelta(days=i))
                v = random.randint(5, 30)
                l = random.randint(1, 10)
                c = random.randint(0, 4)
                s = random.randint(0, 2)
                daily_stats.append((post_id, stat_date, v, l, c, s))

        sql_stat = """INSERT INTO POST_DAILY_STAT (POST_ID, STAT_DATE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT)
                      VALUES (%s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_stat, daily_stats)

        # 5. Contest Winners (For Contest #2 & #1)
        winners_data = [
            (2, 102, hash_id('user2'), 'SUPER_STAR', '🥇 Paw Star 골드 트로피 & 백화점 상품권 50만원'),
            (2, 101, hash_id('user1'), 'RISING_STAR', '🥈 Paw Star 실버 트로피 & 반려동물 용품 30만원'),
            (2, 103, hash_id('user3'), 'BRIGHT_STAR', '🥉 Paw Star 브론즈 트로피 & 고급 사료 세트'),
            (2, 104, hash_id('user4'), 'ROOKIE_STAR', '⭐ 루키 스타 특별상 & 루키 배지'),
            (1, 101, hash_id('user1'), 'SUPER_STAR', '🥇 Paw Star 골드 트로피 & 백화점 상품권 50만원'),
            (1, 102, hash_id('user2'), 'RISING_STAR', '🥈 Paw Star 실버 트로피 & 반려동물 용품 30만원'),
            (1, 103, hash_id('user3'), 'BRIGHT_STAR', '🥉 Paw Star 브론즈 트로피 & 고급 사료 세트'),
            (1, 104, hash_id('user4'), 'ROOKIE_STAR', '⭐ 루키 스타 특별상 & 루키 배지')
        ]
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
