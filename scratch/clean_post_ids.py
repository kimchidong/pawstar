import sys
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def clean_and_consolidate():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # 1. pst_contest_vw 정리
            cur.execute("""
                CREATE TEMPORARY TABLE tmp_vw AS
                SELECT DISTINCT CONTEST_ROUND, 
                       SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1) AS ENT_USER_ID,
                       SUBSTRING_INDEX(VW_USER_ID, '_post_', 1) AS VW_USER_ID,
                       MAX(VW_DT) AS VW_DT
                FROM pst_contest_vw
                GROUP BY CONTEST_ROUND, SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1), SUBSTRING_INDEX(VW_USER_ID, '_post_', 1);
            """)
            cur.execute("TRUNCATE TABLE pst_contest_vw;")
            cur.execute("INSERT INTO pst_contest_vw SELECT * FROM tmp_vw;")

            # 2. pst_contest_like 정리
            cur.execute("""
                CREATE TEMPORARY TABLE tmp_like AS
                SELECT DISTINCT CONTEST_ROUND, 
                       SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1) AS ENT_USER_ID,
                       SUBSTRING_INDEX(LIKE_USER_ID, '_post_', 1) AS LIKE_USER_ID,
                       MAX(LIKE_DT) AS LIKE_DT
                FROM pst_contest_like
                GROUP BY CONTEST_ROUND, SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1), SUBSTRING_INDEX(LIKE_USER_ID, '_post_', 1);
            """)
            cur.execute("TRUNCATE TABLE pst_contest_like;")
            cur.execute("INSERT INTO pst_contest_like SELECT * FROM tmp_like;")

            # 3. pst_contest_cmt 정리
            cur.execute("""
                CREATE TEMPORARY TABLE tmp_cmt AS
                SELECT DISTINCT CONTEST_ROUND, 
                       SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1) AS ENT_USER_ID,
                       SUBSTRING_INDEX(CMT_USER_ID, '_post_', 1) AS CMT_USER_ID,
                       MAX(CMT) AS CMT,
                       MAX(CMD_DT) AS CMD_DT
                FROM pst_contest_cmt
                GROUP BY CONTEST_ROUND, SUBSTRING_INDEX(ENT_USER_ID, '_post_', 1), SUBSTRING_INDEX(CMT_USER_ID, '_post_', 1);
            """)
            cur.execute("TRUNCATE TABLE pst_contest_cmt;")
            cur.execute("INSERT INTO pst_contest_cmt SELECT * FROM tmp_cmt;")

            # 4. pst_contest_round 내 _post_N 서브 레코드 제거
            cur.execute("DELETE FROM pst_contest_round WHERE ENT_USER_ID LIKE '%_post_%';")
            cur.execute("DELETE FROM pst_contest_round WHERE ENT_USER_ID LIKE 'limit_test_user_99_%';")
            cur.execute("""
                INSERT IGNORE INTO pst_contest_round (CONTEST_ROUND, ENT_USER_ID, TITLE, CONTS, SCORE, VW_CNT, LIKE_CNT, CMT_CNT, PHT_PATH, PHT_FILE1)
                VALUES (1, 'limit_test_user_99', '테스트 반려동물', '테스트 게시물입니다.', 20, 10, 2, 1, '/static/image/contest/', 'sample.jpg');
            """)

            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print("=== DB CONSOLIDATION & CLEANUP SUCCESSFUL ===")
    except Exception as e:
        print("Error during consolidation:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    clean_and_consolidate()
