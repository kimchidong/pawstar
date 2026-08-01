import sys
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def recreate_contest_round_table():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

            cur.execute("SHOW COLUMNS FROM pst_contest_round LIKE 'POST_SEQ';")
            if not cur.fetchone():
                cur.execute("DROP TABLE IF EXISTS pst_contest_round_tmp;")
                cur.execute("""
                    CREATE TABLE pst_contest_round_tmp (
                        CONTEST_ROUND INT NOT NULL,
                        ENT_USER_ID VARCHAR(100) NOT NULL,
                        POST_SEQ INT NOT NULL AUTO_INCREMENT,
                        KIND_CD VARCHAR(20) DEFAULT 'K008',
                        PET_NM VARCHAR(50) DEFAULT '',
                        TITLE VARCHAR(150) DEFAULT '',
                        CONTS TEXT,
                        PHT_FILE_PATH1 VARCHAR(255) DEFAULT '',
                        PHT_FILE_PATH2 VARCHAR(255) DEFAULT '',
                        VW_CNT INT DEFAULT 0,
                        LIKE_CNT INT DEFAULT 0,
                        CMT_CNT INT DEFAULT 0,
                        SCORE INT DEFAULT 0,
                        ENT_DT DATETIME DEFAULT CURRENT_TIMESTAMP,
                        TOTAL_RANKING INT DEFAULT NULL,
                        KIND_RANKING INT DEFAULT NULL,
                        PRC_DT DATETIME DEFAULT NULL,
                        PRIMARY KEY (POST_SEQ),
                        KEY idx_round_user (CONTEST_ROUND, ENT_USER_ID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("INSERT INTO pst_contest_round_tmp (CONTEST_ROUND, ENT_USER_ID, KIND_CD, PET_NM, TITLE, CONTS, PHT_FILE_PATH1, PHT_FILE_PATH2, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, ENT_DT, TOTAL_RANKING, KIND_RANKING, PRC_DT) SELECT CONTEST_ROUND, ENT_USER_ID, KIND_CD, PET_NM, TITLE, CONTS, PHT_FILE_PATH1, PHT_FILE_PATH2, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, ENT_DT, TOTAL_RANKING, KIND_RANKING, PRC_DT FROM pst_contest_round;")
                cur.execute("DROP TABLE pst_contest_round;")
                cur.execute("RENAME TABLE pst_contest_round_tmp TO pst_contest_round;")
                print("pst_contest_round table recreated with POST_SEQ AUTO_INCREMENT.")

            for tbl in ['pst_contest_vw', 'pst_contest_like', 'pst_contest_cmt']:
                cur.execute(f"SHOW COLUMNS FROM {tbl} LIKE 'POST_SEQ';")
                if not cur.fetchone():
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN POST_SEQ INT NOT NULL DEFAULT 1;")
                    print(f"Added POST_SEQ to {tbl}")

            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print("=== DB MULTIPLE ENTRIES RECREATION COMPLETE ===")
    except Exception as e:
        print("Recreate error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    recreate_contest_round_table()
