import pymysql
import random
import hashlib
import os
from datetime import datetime, timedelta
import importlib.util

def _get_config_web():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.web.py'),
        os.path.join(curr_dir, '..', 'config.web.py'),
        os.path.join(os.getcwd(), 'config.web.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_web", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.web.py 파일을 찾을 수 없습니다.")

config_web = _get_config_web()
DB_CONFIG = config_web.DB_CONFIG

def hash_id(raw_id):
    return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

def seed_database():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("SET NAMES utf8mb4;")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # 1. db_schema.sql 파일 실행 (테이블 DDL 및 초깃값 생성)
        schema_path = os.path.join(os.path.dirname(__file__), 'db_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_statements = f.read().split(';')
                for stmt in sql_statements:
                    stmt = stmt.strip()
                    if stmt:
                        cur.execute(stmt)

        # 2. 기존 샘플 데이터 정리
        tables = ["USER_BADGE", "CONTEST_WINNER", "POST", "CONTEST", "USERS", "BADGE", "PST_CD"]
        for table in tables:
            try:
                cur.execute(f"TRUNCATE TABLE {table};")
            except Exception:
                pass

        cur.execute("SHOW COLUMNS FROM USERS LIKE 'LAST_LOGIN_AT'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE USERS ADD COLUMN LAST_LOGIN_AT DATETIME DEFAULT CURRENT_TIMESTAMP")
        cur.execute("SHOW COLUMNS FROM USERS LIKE 'LOGIN_COUNT'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE USERS ADD COLUMN LOGIN_COUNT INT DEFAULT 0")

        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 3. Users (USER_ID를 복호화 불가능한 단방향 SHA-256 해시로 저장)
        DEFAULT_AVATAR = '/static/image/profile/default_profile.png'
        users_data = [
            (hash_id('user1'), '몽실이 아빠', DEFAULT_AVATAR, 'USER', '2026-07-30 22:00:00', 5),
            (hash_id('user2'), '냥냥 집사', DEFAULT_AVATAR, 'USER', '2026-07-30 21:00:00', 3),
            (hash_id('user3'), '햄찌마스터', DEFAULT_AVATAR, 'USER', '2026-07-30 20:00:00', 2),
            (hash_id('user4'), '앵두네', DEFAULT_AVATAR, 'USER', '2026-07-30 19:00:00', 1)
        ]
        sql_user = """INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, ROLE, LAST_LOGIN_AT, LOGIN_COUNT)
                      VALUES (%s, %s, %s, %s, %s, %s)"""
        cur.executemany(sql_user, users_data)

        # 4. Contests (7월부터 제1회 시작)
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

        # 5. Badges & User Badges
        badges = [
            (1, '🥇 1위 슈퍼스타', 'trophy-gold', '콘테스트 1위 슈퍼스타'),
            (2, '🥈 2위 브라이트스타', 'trophy-silver', '콘테스트 2위 브라이트스타'),
            (3, '🥉 3위 라이징스타', 'trophy-bronze', '콘테스트 3위 라이징스타'),
            (4, '⭐ 루키스타 1위', 'star-rookie-1', '급상승 루키스타 1위'),
            (5, '⭐ 루키스타 2위', 'star-rookie-2', '급상승 루키스타 2위'),
            (6, '⭐ 루키스타 3위', 'star-rookie-3', '급상승 루키스타 3위')
        ]
        sql_badge = """INSERT INTO BADGE (BADGE_ID, BADGE_NAME, BADGE_ICON, DESCRIPTION) VALUES (%s, %s, %s, %s)"""
        cur.executemany(sql_badge, badges)

        user_badges = [
            (hash_id('user1'), 1, 1),
            (hash_id('user2'), 1, 2),
            (hash_id('user3'), 1, 3),
            (hash_id('user4'), 1, 4)
        ]
        sql_ubadge = """INSERT INTO USER_BADGE (USER_ID, CONTEST_ID, BADGE_ID) VALUES (%s, %s, %s)"""
        cur.executemany(sql_ubadge, user_badges)

        # 6. 공통 코드 테이블 (PST_CD) 데이터 시딩
        pst_cd_data = [
            ('G001C001', 'G001', '진행중'),
            ('G001C002', 'G001', '종료'),
            ('G002P001', 'G002', '전체'),
            ('G002P002', 'G002', '품종')
        ]
        sql_pst_cd = """INSERT INTO PST_CD (CD, GRP, CD_NM) VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE GRP=VALUES(GRP), CD_NM=VALUES(CD_NM)"""
        cur.executemany(sql_pst_cd, pst_cd_data)

        conn.commit()
        print("Successfully seeded all data including PST_CD into DB_PST!")

    except Exception as e:
        conn.rollback()
        print("Error seeding database:", e)
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
