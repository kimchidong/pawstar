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

        # 2. Contests (7월부터 제1회 시작)
        contests_data = [
            (1, '제1회 썸머 파라다이스 펫 콘테스트', '무더위를 싹 씻어줄 시원하고 러블리한 썸머 펫 스타 🌊🍦', '2026-07-01 00:00:00', '2026-07-31 23:59:59', 'IN_PROGRESS', ''),
            (2, '제2회 한여름 밤의 바캉스 펫 챔피언십', '뜨거운 여름 열기보다 더 핫한 인플루언서 펫 축제 🏖️⭐', '2026-08-01 00:00:00', '2026-08-31 23:59:59', 'SCHEDULED', ''),
            (3, '제3회 가을 풍요 펫 콘테스트', '마음까지 넉넉해지는 풍성한 가을 둥글둥글 귀요미들 🍂🌾', '2026-09-01 00:00:00', '2026-09-30 23:59:59', 'SCHEDULED', ''),
            (4, '제4회 할로윈 펌킨 펫 스타전', '귀여운 유령 등장! 심장 멎는 큐트 할로윈 코스튬 파티 🎃👻', '2026-10-01 00:00:00', '2026-10-31 23:59:59', 'SCHEDULED', ''),
            (5, '제5회 단풍 낭만 펫 콘테스트', '바스락 단풍잎과 함께 찾아온 감성 만점 댕냥이 라이프 🍁☕', '2026-11-01 00:00:00', '2026-11-30 23:59:59', 'SCHEDULED', ''),
            (6, '제6회 홀리데이 크리스마스 펫 챔피언십', '메리 크리스마스! 산타 옷 입은 가장 사랑스러운 선물 🎄🎁', '2026-12-01 00:00:00', '2026-12-31 23:59:59', 'SCHEDULED', ''),
            (7, '제7회 새해 맞이 펫스타 콘테스트', '새해 복 많이 받아라냥! 2027년 첫 펫 스타에 도전하세요 🌅', '2027-01-01 00:00:00', '2027-01-31 23:59:59', 'SCHEDULED', ''),
            (8, '제8회 발렌타인 심쿵 콘테스트', '사르르 녹아내리는 우리 아이의 달콤한 심쿵 모먼트 🍫❤️', '2027-02-01 00:00:00', '2027-02-28 23:59:59', 'SCHEDULED', ''),
            (9, '제9회 봄맞이 설렘 펫 콘테스트', '살랑살랑 봄바람 타고 찾아온 미소 천사 펫 스타 🌸🐝', '2027-03-01 00:00:00', '2027-03-31 23:59:59', 'SCHEDULED', ''),
            (10, '제10회 벚꽃 피크닉 펫 챔피언십', '벚꽃 길 따라 화사하게 터지는 댕냥이 피크닉 자랑 🌸🐕', '2027-04-01 00:00:00', '2027-04-30 23:59:59', 'SCHEDULED', ''),
            (11, '제11회 가정의 달 펫 패밀리 콘테스트', '우리 집 보물 1호! 세상에서 가장 따뜻한 펫 가족의 순간 🏡💖', '2027-05-01 00:00:00', '2027-05-31 23:59:59', 'SCHEDULED', ''),
            (12, '제12회 청량 힐링 펫 콘테스트', '초여름 싱그러움 가득! 보기만 해도 힐링되는 펫 스타 🌿🌊', '2027-06-01 00:00:00', '2027-06-30 23:59:59', 'SCHEDULED', '')
        ]
        sql_contest = """INSERT INTO CONTEST (CONTEST_ID, TITLE, DESCRIPTION, START_DATE, END_DATE, STATUS, BANNER_IMG)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_contest, contests_data)

        # 3. Badges & User Badges
        badges = [
            (1, '🥇 1위 슈퍼스타', 'trophy-gold', '콘테스트 1위 슈퍼스타'),
            (2, '🥈 2위 라이징스타', 'trophy-silver', '콘테스트 2위 라이징스타'),
            (3, '🥉 3위 브라이트스타', 'trophy-bronze', '콘테스트 3위 브라이트스타'),
            (4, '⭐ 루키스타 1위', 'star-rookie-1', '급상승 루키스타 1위'),
            (5, '⭐ 루키스타 2위', 'star-rookie-2', '급상승 루키스타 2위'),
            (6, '⭐ 루키스타 3위', 'star-rookie-3', '급상승 루키스타 3위')
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

        # 4. Sample Posts (제1회 콘테스트 테스트용 게시물)
        # SCORE 기준 스타 1~3위와 LIKE_COUNT 기준 루키스타 1~3위가 다르게 추출되는 케이스
        posts_data = [
            (hash_id('user1'), 1, '뽀삐', 'DOG', '오늘의 리트리버 뽀삐', '수영장에서 시원하게 놀았어요 🏊', '/static/uploads/p1.jpg', 'p1.jpg', 'p1_pop.jpg', 'IMAGE', 1000, 50, 50, 20, 5),
            (hash_id('user2'), 1, '나비', 'CAT', '식빵 굽는 나비', '햇살 아래에서 낮잠 타임 ☀️', '/static/uploads/p2.jpg', 'p2.jpg', 'p2_pop.jpg', 'IMAGE', 900, 40, 40, 15, 3),
            (hash_id('user3'), 1, '모찌', 'OTHER', '해바라기씨 먹는 모찌', '볼이 터질 것 같아요 🐹', '/static/uploads/p3.jpg', 'p3.jpg', 'p3_pop.jpg', 'IMAGE', 800, 30, 30, 10, 2),
            (hash_id('user4'), 1, '앵두', 'OTHER', '노래하는 앵두 🦜', '아침마다 기분 좋게 쩨쩨 🎶', '/static/uploads/p4.jpg', 'p4.jpg', 'p4_pop.jpg', 'IMAGE', 200, 500, 500, 8, 1),
            (hash_id('user1'), 1, '뽀삐2', 'DOG', '산책 나온 뽀삐', '신나게 꼬리 흔들기 🐕', '/static/uploads/p5.jpg', 'p5.jpg', 'p5_pop.jpg', 'IMAGE', 150, 400, 400, 5, 0),
            (hash_id('user2'), 1, '나비2', 'CAT', '야옹이 츄르 타임', '츄르 먹고 신난 귀요미 🐱', '/static/uploads/p6.jpg', 'p6.jpg', 'p6_pop.jpg', 'IMAGE', 100, 300, 300, 2, 0),
            (hash_id('user3'), 1, '모찌2', 'OTHER', '쳇바퀴 달리는 모찌', '폭풍 운동 중인 햄찌 💨', '/static/uploads/p7.jpg', 'p7.jpg', 'p7_pop.jpg', 'IMAGE', 50, 20, 20, 1, 0),
            (hash_id('user4'), 1, '앵두2', 'OTHER', '앵두의 조는 모습', '꾸벅꾸벅 졸고 있어요 😴', '/static/uploads/p8.jpg', 'p8.jpg', 'p8_pop.jpg', 'IMAGE', 20, 5, 5, 0, 0)
        ]
        sql_post = """INSERT INTO POST (USER_ID, CONTEST_ID, PET_NAME, PET_TYPE, TITLE, CONTENT, FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, MEDIA_TYPE, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_post, posts_data)

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
