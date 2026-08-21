#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paw Star 매월 1일 대회 당선 및 회차 생성 배치 스크립트

[Crontab 설정 방법]
매월 1일 0시 0분 0초 실행:
0 0 1 * * /usr/bin/python3 /path/to/pawstar/monthly_award_batch.py >> /path/to/pawstar/batch.log 2>&1
"""

import sys
import os
import datetime
import pymysql
import importlib.util

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def _get_config_batch():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.batch.py'),
        os.path.join(curr_dir, '..', 'config.batch.py'),
        os.path.join(os.getcwd(), 'config.batch.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_batch", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.batch.py 파일을 찾을 수 없습니다.")

config_batch = _get_config_batch()
DB_CONFIG = config_batch.DB_CONFIG

from utils.logger import get_batch_logger, hash_ip

batch_logger = get_batch_logger()
LOCAL_HASH = hash_ip('127.0.0.1')
LOG_EXTRA = {'device': 'BATCH', 'ip_hash': LOCAL_HASH}

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        msg = f"Database connection failed: {e}"
        print(f"[{datetime.datetime.now()}] {msg}")
        batch_logger.error(msg, extra=LOG_EXTRA)
        return None

def run_monthly_award_batch():
    now = datetime.datetime.now()
    batch_logger.info("Batch process started: Monthly award & contest round creation.", extra=LOG_EXTRA)

    conn = get_db_connection()
    if not conn:
        batch_logger.error("Batch process failed: Could not connect to DB.", extra=LOG_EXTRA)
        batch_logger.info("Batch process ended with failure.", extra=LOG_EXTRA)
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")

            # 1. 진행 중인 회차 조회 (G001C001)
            batch_logger.info("[Step 1] Fetching active contest round (G001C001)...", extra=LOG_EXTRA)
            cur.execute("""
                SELECT CONTEST_ROUND, THEME_CD, ST_DT, ED_DT
                FROM PST_CONTEST
                WHERE CONTEST_STAT = 'G001C001'
                ORDER BY CONTEST_ROUND DESC
                LIMIT 1
            """)
            current_contest = cur.fetchone()

            if not current_contest:
                batch_logger.info("[Step 1] No active contest round found. Initializing 1st contest round...", extra=LOG_EXTRA)
                current_month = now.month
                target_theme_cd = f'T{current_month:03d}'
                cur.execute("SELECT THEME_CD FROM PST_THEME WHERE THEME_CD = %s", (target_theme_cd,))
                theme_row = cur.fetchone()
                if not theme_row:
                    target_theme_cd = 'T001'

                cur.execute("""
                    INSERT INTO PST_CONTEST (CONTEST_ROUND, THEME_CD, ST_DT, ED_DT, CONTEST_STAT)
                    VALUES (1, %s, NOW(), CONCAT(LAST_DAY(NOW()), ' 23:59:59'), 'G001C001')
                    ON DUPLICATE KEY UPDATE THEME_CD = VALUES(THEME_CD), ED_DT = VALUES(ED_DT), CONTEST_STAT = 'G001C001'
                """, (target_theme_cd,))
                conn.commit()
                batch_logger.info(f"[Step 1] 1st contest round created successfully with theme {target_theme_cd}.", extra=LOG_EXTRA)
                batch_logger.info("Batch process completed successfully.", extra=LOG_EXTRA)
                batch_logger.info("Batch process ended.", extra=LOG_EXTRA)
                conn.close()
                return

            round_id = current_contest['CONTEST_ROUND']
            batch_logger.info(f"[Step 1] Active contest round fetched: Round #{round_id}.", extra=LOG_EXTRA)

            # 2. 해당 회차 모든 참가물의 실시간 DB 이력 재집계 및 점수(SCORE) 산출
            batch_logger.info(f"[Step 2] Recalculating participant metrics and scores for Round #{round_id}...", extra=LOG_EXTRA)
            cur.execute("""
                SELECT 
                    R.CONTEST_ROUND, 
                    R.ROUND_NO, 
                    R.ENT_USER_ID, 
                    R.KIND_CD,
                    R.SHARE_CNT,
                    (SELECT COUNT(*) FROM PST_CONTEST_VW V WHERE V.CONTEST_ROUND = R.CONTEST_ROUND AND V.ROUND_NO = R.ROUND_NO) AS REAL_VW_CNT,
                    (SELECT COUNT(*) FROM PST_CONTEST_LIKE L WHERE L.CONTEST_ROUND = R.CONTEST_ROUND AND L.ROUND_NO = R.ROUND_NO) AS REAL_LIKE_CNT,
                    (SELECT COUNT(*) FROM PST_CONTEST_CMT C WHERE C.CONTEST_ROUND = R.CONTEST_ROUND AND C.ROUND_NO = R.ROUND_NO) AS REAL_CMT_CNT,
                    GREATEST(
                        COALESCE((SELECT COUNT(*) FROM PST_CONTEST_SHARE S WHERE S.CONTEST_ROUND = R.CONTEST_ROUND AND S.ROUND_NO = R.ROUND_NO), 0),
                        COALESCE(R.SHARE_CNT, 0)
                    ) AS REAL_SHARE_CNT,
                    ((SELECT COUNT(*) FROM PST_CONTEST_VW V WHERE V.CONTEST_ROUND = R.CONTEST_ROUND AND V.ROUND_NO = R.ROUND_NO) * 1 +
                     (SELECT COUNT(*) FROM PST_CONTEST_LIKE L WHERE L.CONTEST_ROUND = R.CONTEST_ROUND AND L.ROUND_NO = R.ROUND_NO) * 5 +
                     (SELECT COUNT(*) FROM PST_CONTEST_CMT C WHERE C.CONTEST_ROUND = R.CONTEST_ROUND AND C.ROUND_NO = R.ROUND_NO) * 10 +
                     GREATEST(
                         COALESCE((SELECT COUNT(*) FROM PST_CONTEST_SHARE S WHERE S.CONTEST_ROUND = R.CONTEST_ROUND AND S.ROUND_NO = R.ROUND_NO), 0),
                         COALESCE(R.SHARE_CNT, 0)
                     ) * 10) AS CALC_SCORE
                FROM PST_CONTEST_ROUND R
                WHERE R.CONTEST_ROUND = %s
            """, (round_id,))
            participants = cur.fetchall()

            batch_logger.info(f"[Step 2] Total participant entries to update: {len(participants)}.", extra=LOG_EXTRA)

            for p in participants:
                calc_score = p['CALC_SCORE']
                real_vw = p['REAL_VW_CNT']
                real_like = p['REAL_LIKE_CNT']
                real_cmt = p['REAL_CMT_CNT']
                real_share = p['REAL_SHARE_CNT']
                cur.execute("""
                    UPDATE PST_CONTEST_ROUND
                    SET VW_CNT = %s, LIKE_CNT = %s, CMT_CNT = %s, SHARE_CNT = %s, SCORE = %s
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (real_vw, real_like, real_cmt, real_share, calc_score, round_id, p['ROUND_NO']))
            
            batch_logger.info("[Step 2] Metric recalculation completed.", extra=LOG_EXTRA)

            # 3. 전체 순위(TOTAL_RANKING) 산출 & 저장
            batch_logger.info("[Step 3] Calculating and saving overall total rankings...", extra=LOG_EXTRA)
            cur.execute("""
                SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SHARE_CNT, SCORE
                FROM PST_CONTEST_ROUND
                WHERE CONTEST_ROUND = %s
                ORDER BY SCORE DESC, CMT_CNT DESC, LIKE_CNT DESC, VW_CNT DESC, SHARE_CNT DESC, ENT_DT ASC
            """, (round_id,))
            total_sorted = cur.fetchall()

            current_rank = 1
            prev_key = None
            total_sorted_with_rank = []

            for item in total_sorted:
                key = (item['SCORE'], item['CMT_CNT'], item['LIKE_CNT'], item['VW_CNT'], item.get('SHARE_CNT', 0))
                if prev_key is not None and key != prev_key:
                    current_rank += 1
                
                item['rank'] = current_rank
                prev_key = key
                total_sorted_with_rank.append(item)

                cur.execute("""
                    UPDATE PST_CONTEST_ROUND
                    SET TOTAL_RANKING = %s, PRC_DT = NOW()
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (current_rank, round_id, item['ROUND_NO']))
            
            batch_logger.info("[Step 3] Overall total rankings saved.", extra=LOG_EXTRA)

            # 4. 품종별 순위(KIND_RANKING) 산출 & 저장
            batch_logger.info("[Step 4] Calculating and saving category kind rankings...", extra=LOG_EXTRA)
            cur.execute("""
                SELECT DISTINCT KIND_CD FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND KIND_CD IS NOT NULL
            """, (round_id,))
            kind_rows = cur.fetchall()

            kind_sorted_with_rank_dict = {}

            for k_row in kind_rows:
                k_cd = k_row['KIND_CD']
                cur.execute("""
                    SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                    FROM PST_CONTEST_ROUND
                    WHERE CONTEST_ROUND = %s AND KIND_CD = %s
                    ORDER BY SCORE DESC, CMT_CNT DESC, LIKE_CNT DESC, VW_CNT DESC, ENT_DT ASC
                """, (round_id, k_cd))
                k_sorted = cur.fetchall()

                k_rank = 1
                k_prev_key = None
                k_list = []

                for k_item in k_sorted:
                    k_key = (k_item['SCORE'], k_item['CMT_CNT'], k_item['LIKE_CNT'], k_item['VW_CNT'])
                    if k_prev_key is not None and k_key != k_prev_key:
                        k_rank += 1
                    
                    k_item['rank'] = k_rank
                    k_prev_key = k_key
                    k_list.append(k_item)

                    cur.execute("""
                        UPDATE PST_CONTEST_ROUND
                        SET KIND_RANKING = %s
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                    """, (k_rank, round_id, k_item['ROUND_NO']))

                kind_sorted_with_rank_dict[k_cd] = k_list
            
            batch_logger.info("[Step 4] Category kind rankings saved.", extra=LOG_EXTRA)

            # 5. 당선자 레코드 (PST_CONTEST_AWARD) INSERT
            batch_logger.info("[Step 5] Inserting contest award records for overall & kind top winners...", extra=LOG_EXTRA)
            award_codes_overall = {1: 'P001A101', 2: 'P001A102', 3: 'P001A103'}
            top_overall = [item for item in total_sorted_with_rank if item['rank'] <= 3]

            for item in top_overall:
                r_val = item['rank']
                award_cd = award_codes_overall.get(r_val, 'P001A103')
                cur.execute("""
                    INSERT INTO PST_CONTEST_AWARD
                    (CONTEST_ROUND, ROUND_NO, AWARD_PART, AWARD_CD, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                    VALUES (%s, %s, 'G002P001', %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        KIND_CD=VALUES(KIND_CD),
                        VW_CNT=VALUES(VW_CNT),
                        LIKE_CNT=VALUES(LIKE_CNT),
                        CMT_CNT=VALUES(CMT_CNT),
                        SCORE=VALUES(SCORE), 
                        RANKING=VALUES(RANKING), 
                        ENT_USER_ID=VALUES(ENT_USER_ID)
                """, (round_id, item['ROUND_NO'], award_cd, item['ENT_USER_ID'], item['KIND_CD'], item['VW_CNT'], item['LIKE_CNT'], item['CMT_CNT'], item['SCORE'], r_val))

            award_codes_kind = {1: 'P002A901', 2: 'P002A902', 3: 'P002A903'}
            for k_cd, k_list in kind_sorted_with_rank_dict.items():
                k_top = [item for item in k_list if item['rank'] <= 3]
                for item in k_top:
                    r_val = item['rank']
                    award_cd = award_codes_kind.get(r_val, 'P002A903')
                    cur.execute("""
                        INSERT INTO PST_CONTEST_AWARD
                        (CONTEST_ROUND, ROUND_NO, AWARD_PART, AWARD_CD, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                        VALUES (%s, %s, 'G002P002', %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            KIND_CD=VALUES(KIND_CD),
                            VW_CNT=VALUES(VW_CNT),
                            LIKE_CNT=VALUES(LIKE_CNT),
                            CMT_CNT=VALUES(CMT_CNT),
                            SCORE=VALUES(SCORE), 
                            RANKING=VALUES(RANKING), 
                            ENT_USER_ID=VALUES(ENT_USER_ID)
                    """, (round_id, item['ROUND_NO'], award_cd, item['ENT_USER_ID'], item['KIND_CD'], item['VW_CNT'], item['LIKE_CNT'], item['CMT_CNT'], item['SCORE'], r_val))

            batch_logger.info("[Step 5] Contest award records inserted successfully.", extra=LOG_EXTRA)

            # 6. 현재 회차 종료 (G001C002) 처리
            batch_logger.info(f"[Step 6] Closing active contest round #{round_id}...", extra=LOG_EXTRA)
            cur.execute("""
                UPDATE PST_CONTEST
                SET CONTEST_STAT = 'G001C002'
                WHERE CONTEST_ROUND = %s
            """, (round_id,))

            # 7. 다음 회차 생성
            next_round = round_id + 1
            current_month = now.month
            target_theme_cd = f'T{current_month:03d}'

            cur.execute("SELECT THEME_CD FROM PST_THEME WHERE THEME_CD = %s", (target_theme_cd,))
            theme_row = cur.fetchone()
            if not theme_row:
                target_theme_cd = 'T001'

            cur.execute("""
                INSERT INTO PST_CONTEST (CONTEST_ROUND, THEME_CD, ST_DT, ED_DT, CONTEST_STAT)
                VALUES (%s, %s, NOW(), CONCAT(LAST_DAY(NOW()), ' 23:59:59'), 'G001C001')
                ON DUPLICATE KEY UPDATE THEME_CD = VALUES(THEME_CD), ED_DT = VALUES(ED_DT), CONTEST_STAT = 'G001C001'
            """, (next_round, target_theme_cd))

            conn.commit()
            batch_logger.info(f"[Step 7] Next contest round #{next_round} created with theme {target_theme_cd}.", extra=LOG_EXTRA)
            batch_logger.info("Batch process completed successfully.", extra=LOG_EXTRA)
            batch_logger.info("Batch process ended.", extra=LOG_EXTRA)
            conn.close()

    except Exception as e:
        msg = f"Batch process failed with error: {e}"
        print(f"[{now}] {msg}")
        batch_logger.error(msg, extra=LOG_EXTRA)
        batch_logger.info("Batch process ended with failure.", extra=LOG_EXTRA)
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == '__main__':
    run_monthly_award_batch()
