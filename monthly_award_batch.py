#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paw Star 매월 1일 대회 당선 및 회차 생성 배치 스크립트

[Crontab 설정 방법]
매월 1일 0시 0분 0초 실행:
0 0 1 * * /usr/bin/python3 /path/to/pawstar/monthly_award_batch.py >> /path/to/pawstar/batch.log 2>&1

[업무 처리 내용]
1. 현재 진행 중(G001C001) 회차 조회
2. 해당 회차 참가자 전원의 점수(SCORE) 계산
3. 전체 순위(TOTAL_RANKING) 및 품종별 순위(KIND_RANKING) 산출 및 pst_contest_round 저장 (PRC_DT 동결)
4. 수상자 레코드(pst_contest_award) INSERT
   - 전체 1~3위 (G002P001: P001A101, P001A102, P001A103)
   - 품종별 1~3위 (G002P002: P002A901, P002A902, P002A903)
5. 진행 중 회차 상태 종료(G001C002) 처리
6. 다음 월 테마(pst_theme)를 기반으로 새 회차(G001C001) 자동 생성
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
        print(f"[{datetime.datetime.now()}] DB 연결 실패: {e}")
        return None

def run_monthly_award_batch():
    now = datetime.datetime.now()
    print("==================================================")
    print(f"[{now}] PAW STAR 월간 당선 & 회차 생성 배치 실행")
    print("==================================================")

    conn = get_db_connection()
    if not conn:
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")

            # 1. 진행 중인 회차 조회 (G001C001)
            cur.execute("""
                SELECT CONTEST_ROUND, THEME_CD, ST_DT, ED_DT
                FROM pst_contest
                WHERE CONTEST_STAT = 'G001C001'
                ORDER BY CONTEST_ROUND DESC
                LIMIT 1
            """)
            current_contest = cur.fetchone()

            if not current_contest:
                print(f"[{now}] 진행 중인 회차가 없어 회차 #1 자동 생성을 진행합니다.")
                cur.execute("""
                    INSERT INTO pst_contest (CONTEST_ROUND, THEME_CD, ST_DT, ED_DT, CONTEST_STAT)
                    VALUES (1, 'T001', NOW(), DATE_ADD(NOW(), INTERVAL 1 MONTH), 'G001C001')
                """)
                conn.commit()
                cur.execute("""
                    SELECT CONTEST_ROUND, THEME_CD, ST_DT, ED_DT
                    FROM pst_contest WHERE CONTEST_ROUND = 1
                """)
                current_contest = cur.fetchone()

            round_id = current_contest['CONTEST_ROUND']
            print(f"[{now}] 대상 콘테스트 회차: 제{round_id}회")

            # 2. 해당 회차 모든 참가물의 실시간 DB 이력(조회/좋아요/댓글) 재집계 및 점수(SCORE) 산출
            cur.execute("""
                SELECT 
                    r.CONTEST_ROUND, 
                    r.ROUND_NO, 
                    r.ENT_USER_ID, 
                    r.KIND_CD,
                    (SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) AS REAL_VW_CNT,
                    (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) AS REAL_LIKE_CNT,
                    (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) AS REAL_CMT_CNT,
                    ((SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) * 1 +
                     (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) * 5 +
                     (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) * 10) AS CALC_SCORE
                FROM pst_contest_round r
                WHERE r.CONTEST_ROUND = %s
            """, (round_id,))
            participants = cur.fetchall()

            print(f"[{now}] 총 참가 작품 수: {len(participants)}개")

            for p in participants:
                calc_score = p['CALC_SCORE']
                real_vw = p['REAL_VW_CNT']
                real_like = p['REAL_LIKE_CNT']
                real_cmt = p['REAL_CMT_CNT']
                cur.execute("""
                    UPDATE pst_contest_round
                    SET VW_CNT = %s, LIKE_CNT = %s, CMT_CNT = %s, SCORE = %s
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (real_vw, real_like, real_cmt, calc_score, round_id, p['ROUND_NO']))

            # 3. 전체 순위(TOTAL_RANKING) 산출 & 저장
            cur.execute("""
                SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                FROM pst_contest_round
                WHERE CONTEST_ROUND = %s
                ORDER BY SCORE DESC, ENT_DT ASC
            """, (round_id,))
            total_sorted = cur.fetchall()

            for rank_idx, item in enumerate(total_sorted, start=1):
                cur.execute("""
                    UPDATE pst_contest_round
                    SET TOTAL_RANKING = %s, PRC_DT = NOW()
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (rank_idx, round_id, item['ROUND_NO']))

            # 4. 품종별 순위(KIND_RANKING) 산출 & 저장
            cur.execute("""
                SELECT DISTINCT KIND_CD FROM pst_contest_round WHERE CONTEST_ROUND = %s AND KIND_CD IS NOT NULL
            """, (round_id,))
            kind_rows = cur.fetchall()

            for k_row in kind_rows:
                k_cd = k_row['KIND_CD']
                cur.execute("""
                    SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                    FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND KIND_CD = %s
                    ORDER BY SCORE DESC, ENT_DT ASC
                """, (round_id, k_cd))
                k_sorted = cur.fetchall()
                for k_rank, k_item in enumerate(k_sorted, start=1):
                    cur.execute("""
                        UPDATE pst_contest_round
                        SET KIND_RANKING = %s
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                    """, (k_rank, round_id, k_item['ROUND_NO']))

            # 5. 당선자 레코드 (pst_contest_award) INSERT (VW_CNT, LIKE_CNT, CMT_CNT 저장 포함)
            award_codes_overall = ['P001A101', 'P001A102', 'P001A103']
            for rank_idx, item in enumerate(total_sorted[:3], start=1):
                award_cd = award_codes_overall[rank_idx - 1]
                cur.execute("""
                    INSERT INTO pst_contest_award
                    (CONTEST_ROUND, ROUND_NO, AWARD_PART, AWARD_CD, ENT_USER_ID, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                    VALUES (%s, %s, 'G002P001', %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        VW_CNT=VALUES(VW_CNT),
                        LIKE_CNT=VALUES(LIKE_CNT),
                        CMT_CNT=VALUES(CMT_CNT),
                        SCORE=VALUES(SCORE), 
                        RANKING=VALUES(RANKING), 
                        ENT_USER_ID=VALUES(ENT_USER_ID)
                """, (round_id, item['ROUND_NO'], award_cd, item['ENT_USER_ID'], item['VW_CNT'], item['LIKE_CNT'], item['CMT_CNT'], item['SCORE'], rank_idx))

            award_codes_kind = ['P002A901', 'P002A902', 'P002A903']
            for k_row in kind_rows:
                k_cd = k_row['KIND_CD']
                cur.execute("""
                    SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                    FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND KIND_CD = %s
                    ORDER BY SCORE DESC, ENT_DT ASC
                    LIMIT 3
                """, (round_id, k_cd))
                k_top = cur.fetchall()
                for rank_idx, item in enumerate(k_top, start=1):
                    award_cd = award_codes_kind[rank_idx - 1]
                    cur.execute("""
                        INSERT INTO pst_contest_award
                        (CONTEST_ROUND, ROUND_NO, AWARD_PART, AWARD_CD, ENT_USER_ID, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                        VALUES (%s, %s, 'G002P002', %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            VW_CNT=VALUES(VW_CNT),
                            LIKE_CNT=VALUES(LIKE_CNT),
                            CMT_CNT=VALUES(CMT_CNT),
                            SCORE=VALUES(SCORE), 
                            RANKING=VALUES(RANKING), 
                            ENT_USER_ID=VALUES(ENT_USER_ID)
                    """, (round_id, item['ROUND_NO'], award_cd, item['ENT_USER_ID'], item['VW_CNT'], item['LIKE_CNT'], item['CMT_CNT'], item['SCORE'], rank_idx))

            # 6. 현재 회차 종료 (G001C002) 처리
            cur.execute("""
                UPDATE pst_contest
                SET CONTEST_STAT = 'G001C002'
                WHERE CONTEST_ROUND = %s
            """, (round_id,))

            # 7. 다음 회차 (CONTEST_ROUND + 1) 생성 (G001C001)
            next_round = round_id + 1
            next_month = (now.month % 12) + 1
            next_theme_cd = f'T{next_month:03d}'

            cur.execute("""
                INSERT INTO pst_contest (CONTEST_ROUND, THEME_CD, ST_DT, ED_DT, CONTEST_STAT)
                VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 1 MONTH), 'G001C001')
                ON DUPLICATE KEY UPDATE CONTEST_STAT = 'G001C001'
            """, (next_round, next_theme_cd))

            conn.commit()
            print(f"[{now}] 제{round_id}회 마감 및 당선자 선정 완료! 제{next_round}회(테마: {next_theme_cd}) 진행중으로 새로 오픈되었습니다.")
            conn.close()

    except Exception as e:
        print(f"[{now}] 배치 실패: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == '__main__':
    run_monthly_award_batch()
