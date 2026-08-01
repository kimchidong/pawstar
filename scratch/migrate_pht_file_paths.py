import sys
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def migrate_full_file_paths():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_FILE_PATH1 = CONCAT('/static/image/paw/2026/08/', PHT_FILE_PATH1)
                WHERE PHT_FILE_PATH1 NOT LIKE '/%';
            """)

            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_FILE_PATH2 = CONCAT('/static/image/paw/2026/08/', PHT_FILE_PATH2)
                WHERE PHT_FILE_PATH2 NOT LIKE '/%';
            """)

            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_FILE_PATH2 = PHT_FILE_PATH1
                WHERE PHT_FILE_PATH2 IS NULL OR PHT_FILE_PATH2 = '';
            """)

            conn.commit()
            print("=== DB PHT_FILE_PATH1 & PHT_FILE_PATH2 FULL PATH MIGRATION COMPLETE ===")
    except Exception as e:
        print("Migration Error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_full_file_paths()
