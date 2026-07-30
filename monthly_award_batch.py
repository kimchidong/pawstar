#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paw Star 매월 1일 대회 당선 로직 배치 스크립트

[Crontab 설정 방법]
매월 1일 0시 0분 0초 실행:
0 0 1 * * /usr/bin/python3 /path/to/pawstar/monthly_award_batch.py >> /path/to/pawstar/batch.log 2>&1

[처리 내용]
1. 진행 중이었던 지난달 회차(CONTEST) 선정 및 상태 종료(CLOSED) 처리
2. 해당 회차의 게시물(POST) 중 하트(LIKE_COUNT/SCORE) 기준 순위 산출:
   - 스타 1위, 2위, 3위 (RANKING 1, 2, 3)
   - 루키스타 3마리 (상위 1~3위 제외 후 하트 순 1, 2, 3위 -> RANKING 4, 5, 6)
3. 당선 결과를 POST 테이블의 RANKING (전체순위) 및 BADGE_ID 컬럼에 UPDATE 저장
4. (연동) CONTEST_WINNER 및 USER_BADGE 테이블에도 수상 기록 보장
"""

import sys
import os
import datetime
import pymysql

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from config import db_config

def get_db_connection():
    try:
        return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ DB 연결 실패: {e}")
        return None

def ensure_schema(conn):
    """ POST 테이블에 RANKING 및 BADGE_ID 컬럼 자가 점검 및 마이그레이션 """
    with conn.cursor() as cur:
        # 기존 `RANK` 컬럼이 남아있다면 `RANKING`으로 컬럼명 변경
        cur.execute("SHOW COLUMNS FROM POST LIKE 'RANK'")
        if cur.fetchone():
            print(f"[{datetime.datetime.now()}] ⚙️ POST 테이블의 RANK 컬럼을 RANKING으로 변경 중...")
            cur.execute("ALTER TABLE POST CHANGE COLUMN `RANK` RANKING INT DEFAULT NULL")

        # POST 테이블에 RANKING 컬럼 존재 여부 체크 및 추가
        cur.execute("SHOW COLUMNS FROM POST LIKE 'RANKING'")
        if not cur.fetchone():
            print(f"[{datetime.datetime.now()}] ⚙️ POST 테이블에 RANKING 컬럼 추가 중...")
            cur.execute("ALTER TABLE POST ADD COLUMN RANKING INT DEFAULT NULL")

        cur.execute("SHOW COLUMNS FROM POST LIKE 'BADGE_ID'")
        if not cur.fetchone():
            print(f"[{datetime.datetime.now()}] ⚙️ POST 테이블에 BADGE_ID 컬럼 추가 중...")
            cur.execute("ALTER TABLE POST ADD COLUMN BADGE_ID INT DEFAULT NULL")

        # 필수 BADGE 기본데이터 보장
        badges = [
            (1, '🥇 1위 슈퍼스타', 'trophy-gold', '콘테스트 1위 슈퍼스타'),
            (2, '🥈 2위 라이징스타', 'trophy-silver', '콘테스트 2위 라이징스타'),
            (3, '🥉 3위 브라이트스타', 'trophy-bronze', '콘테스트 3위 브라이트스타'),
            (4, '⭐ 루키스타 1위', 'star-rookie-1', '급상승 루키스타 1위'),
            (5, '⭐ 루키스타 2위', 'star-rookie-2', '급상승 루키스타 2위'),
            (6, '⭐ 루키스타 3위', 'star-rookie-3', '급상승 루키스타 3위'),
        ]
        for badge_id, name, icon, desc in badges:
            cur.execute("""
                INSERT INTO BADGE (BADGE_ID, BADGE_NAME, BADGE_ICON, DESCRIPTION)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE BADGE_NAME=%s, BADGE_ICON=%s, DESCRIPTION=%s
            """, (badge_id, name, icon, desc, name, icon, desc))
    conn.commit()

def run_monthly_award_batch():
    now = datetime.datetime.now()
    print(f"==================================================")
    print(f"[{now}] 🏆 월간 파라다이스 콘테스트 당선 배치 처리 시작")
    print(f"==================================================")

    conn = get_db_connection()
    if not conn:
        sys.exit(1)

    try:
        ensure_schema(conn)

        with conn.cursor() as cur:
            # 1. 진행 중이었던 지난달 회차 찾기
            # 우선순위: STATUS = 'IN_PROGRESS' 인 가장 최근 회차, 없을 시 END_DATE가 현재 이전인 가장 최근 회차
            cur.execute("""
                SELECT CONTEST_ID, TITLE, START_DATE, END_DATE, STATUS 
                FROM CONTEST
                WHERE STATUS = 'IN_PROGRESS'
                ORDER BY CONTEST_ID ASC
                LIMIT 1
            """)
            target_contest = cur.fetchone()

            if not target_contest:
                # IN_PROGRESS가 없는 경우 최신 종료 대상 회차 조회
                cur.execute("""
                    SELECT CONTEST_ID, TITLE, START_DATE, END_DATE, STATUS 
                    FROM CONTEST
                    ORDER BY CONTEST_ID DESC
                    LIMIT 1
                """)
                target_contest = cur.fetchone()

            if not target_contest:
                print(f"[{now}] ⚠️ 진행 대상 콘테스트 회차가 존재하지 않습니다.")
                return

            contest_id = target_contest['CONTEST_ID']
            contest_title = target_contest['TITLE']
            print(f"[{now}] 🎯 대상 회차 선정: [ID: {contest_id}] {contest_title}")

            # 해당 회차 상태를 'CLOSED' (종료) 로 업데이트
            cur.execute("UPDATE CONTEST SET STATUS = 'CLOSED' WHERE CONTEST_ID = %s", (contest_id,))
            print(f"[{now}] 🔒 회차 STATUS를 'CLOSED'로 변경 완료.")

            # 다음 달 예정(SCHEDULED) 회차가 있다면 'IN_PROGRESS'로 변경
            cur.execute("""
                UPDATE CONTEST 
                SET STATUS = 'IN_PROGRESS' 
                WHERE STATUS = 'SCHEDULED' 
                ORDER BY CONTEST_ID ASC 
                LIMIT 1
            """)

            # 2. 스타 1~3위 선정 (SCORE 기준: SCORE DESC, LIKE_COUNT DESC, CREATED_AT ASC)
            cur.execute("""
                SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                FROM POST
                WHERE CONTEST_ID = %s
                ORDER BY SCORE DESC, LIKE_COUNT DESC, CREATED_AT ASC
                LIMIT 3
            """, (contest_id,))
            star_posts = cur.fetchall()

            star_post_ids = [p['POST_ID'] for p in star_posts]

            # 3. 루키스타 3마리 선정 (1~3위 스타 제외, 오로지 하트 기준: LIKE_COUNT DESC, SCORE DESC, CREATED_AT ASC)
            if star_post_ids:
                format_strings = ','.join(['%s'] * len(star_post_ids))
                rookie_sql = f"""
                    SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                    FROM POST
                    WHERE CONTEST_ID = %s
                      AND POST_ID NOT IN ({format_strings})
                    ORDER BY LIKE_COUNT DESC, SCORE DESC, CREATED_AT ASC
                    LIMIT 3
                """
                cur.execute(rookie_sql, [contest_id] + star_post_ids)
            else:
                cur.execute("""
                    SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                    FROM POST
                    WHERE CONTEST_ID = %s
                    ORDER BY LIKE_COUNT DESC, SCORE DESC, CREATED_AT ASC
                    LIMIT 3
                """, (contest_id,))
            rookie_posts = cur.fetchall()

            if not star_posts and not rookie_posts:
                print(f"[{now}] ⚠️ 대상 회차({contest_id})에 등록된 게시물이 없습니다.")
                conn.commit()
                return

            print(f"[{now}] 📊 스타 3위(점수 기준) 및 루키스타 3마리(하트 기준) 선정 시작.")

            star_awards = [
                (1, 1, 'SUPER_STAR', '🥇 스타 1위 (슈퍼스타)'),
                (2, 2, 'RISING_STAR', '🥈 스타 2위 (라이징스타)'),
                (3, 3, 'BRIGHT_STAR', '🥉 스타 3위 (브라이트스타)'),
            ]

            rookie_awards = [
                (4, 4, 'ROOKIE_STAR_1', '⭐ 루키스타 1위'),
                (5, 5, 'ROOKIE_STAR_2', '⭐ 루키스타 2위'),
                (6, 6, 'ROOKIE_STAR_3', '⭐ 루키스타 3위'),
            ]

            awarded_count = 0

            # 스타 1~3위 업데이트
            for idx, post in enumerate(star_posts):
                rank_val, badge_id, award_type, award_label = star_awards[idx]
                post_id = post['POST_ID']
                user_id = post['USER_ID']
                pet_name = post['PET_NAME']
                score = post['SCORE']
                like_cnt = post['LIKE_COUNT']

                cur.execute("UPDATE POST SET RANKING = %s, BADGE_ID = %s WHERE POST_ID = %s", (rank_val, badge_id, post_id))
                cur.execute("""
                    INSERT INTO CONTEST_WINNER (CONTEST_ID, POST_ID, USER_ID, AWARD_TYPE, PRIZE_NAME)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE AWARD_TYPE = VALUES(AWARD_TYPE)
                """, (contest_id, post_id, user_id, award_type, award_label))
                cur.execute("""
                    INSERT INTO USER_BADGE (USER_ID, CONTEST_ID, BADGE_ID)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE GRANTED_AT = CURRENT_TIMESTAMP
                """, (user_id, contest_id, badge_id))
                awarded_count += 1
                print(f"  [{award_label}] 순위: {rank_val}위 | 게시물 ID: {post_id} | 반려동물: {pet_name} | 점수: {score}점 | 하트: {like_cnt}개 | BADGE_ID: {badge_id}")

            # 루키스타 1~3위 (하트 순) 업데이트
            for idx, post in enumerate(rookie_posts):
                rank_val, badge_id, award_type, award_label = rookie_awards[idx]
                post_id = post['POST_ID']
                user_id = post['USER_ID']
                pet_name = post['PET_NAME']
                score = post['SCORE']
                like_cnt = post['LIKE_COUNT']

                cur.execute("UPDATE POST SET RANKING = %s, BADGE_ID = %s WHERE POST_ID = %s", (rank_val, badge_id, post_id))
                cur.execute("""
                    INSERT INTO CONTEST_WINNER (CONTEST_ID, POST_ID, USER_ID, AWARD_TYPE, PRIZE_NAME)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE AWARD_TYPE = VALUES(AWARD_TYPE)
                """, (contest_id, post_id, user_id, award_type, award_label))
                cur.execute("""
                    INSERT INTO USER_BADGE (USER_ID, CONTEST_ID, BADGE_ID)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE GRANTED_AT = CURRENT_TIMESTAMP
                """, (user_id, contest_id, badge_id))
                awarded_count += 1
                print(f"  [{award_label}] 순위: {rank_val}위 | 게시물 ID: {post_id} | 반려동물: {pet_name} | 하트: {like_cnt}개 | 점수: {score}점 | BADGE_ID: {badge_id}")

            # 3-2. 동물 종류별 1, 2, 3위 (강아지 1위, 고양이 1위, 햄스터 1위 등) 선정
            categories = ['강아지', '고양이', '햄스터', '앵무새', '토끼']
            for cat in categories:
                cur.execute("""
                    SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                    FROM POST
                    WHERE CONTEST_ID = %s AND PET_TYPE LIKE %s
                    ORDER BY SCORE DESC, LIKE_COUNT DESC, CREATED_AT ASC
                    LIMIT 3
                """, (contest_id, f"%{cat}%"))
                cat_posts = cur.fetchall()
                for idx, post in enumerate(cat_posts):
                    rank_num = idx + 1
                    award_type = f"CAT_{cat}_{rank_num}"
                    award_label = f"{cat} {rank_num}위"
                    cur.execute("""
                        INSERT INTO CONTEST_WINNER (CONTEST_ID, POST_ID, USER_ID, AWARD_TYPE, PRIZE_NAME)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE PRIZE_NAME = VALUES(PRIZE_NAME)
                    """, (contest_id, post['POST_ID'], post['USER_ID'], award_type, award_label))
                    print(f"  [{award_label}] 게시물 ID: {post['POST_ID']} | 반려동물: {post['PET_NAME']} | 점수: {post['SCORE']}점")

            # 4. 1~6위 당선작 외의 모든 남아있는 게시물 순위(RANKING) 순차 부여 (7위, 8위, ...)
            awarded_post_ids = star_post_ids + [p['POST_ID'] for p in rookie_posts]
            if awarded_post_ids:
                format_strings = ','.join(['%s'] * len(awarded_post_ids))
                other_sql = f"""
                    SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                    FROM POST
                    WHERE CONTEST_ID = %s
                      AND POST_ID NOT IN ({format_strings})
                    ORDER BY LIKE_COUNT DESC, SCORE DESC, CREATED_AT ASC
                """
                cur.execute(other_sql, [contest_id] + awarded_post_ids)
            else:
                cur.execute("""
                    SELECT POST_ID, USER_ID, PET_NAME, TITLE, LIKE_COUNT, SCORE
                    FROM POST
                    WHERE CONTEST_ID = %s
                    ORDER BY LIKE_COUNT DESC, SCORE DESC, CREATED_AT ASC
                """, (contest_id,))

            other_posts = cur.fetchall()

            current_rank = len(awarded_post_ids) + 1
            for post in other_posts:
                post_id = post['POST_ID']
                pet_name = post['PET_NAME']
                score = post['SCORE']
                like_cnt = post['LIKE_COUNT']

                cur.execute("UPDATE POST SET RANKING = %s, BADGE_ID = NULL WHERE POST_ID = %s", (current_rank, post_id))
                print(f"  [참가 게시물] 순위: {current_rank}위 | 게시물 ID: {post_id} | 반려동물: {pet_name} | 하트: {like_cnt}개 | 점수: {score}점 | BADGE_ID: None")
                current_rank += 1

            conn.commit()
            print(f"[{datetime.datetime.now()}] ✅ 회차 내 전체 총 {awarded_count + len(other_posts)}개 게시물 순위(RANKING) 반영 및 당선 정보 UPDATE 완료!")

    except Exception as err:
        conn.rollback()
        print(f"[{datetime.datetime.now()}] ❌ 배치 실행 중 오류 발생: {err}")
        raise err
    finally:
        conn.close()

if __name__ == '__main__':
    run_monthly_award_batch()
