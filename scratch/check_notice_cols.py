import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.contest_service import service

def check_notice_columns():
    conn = service.get_db_connection()
    if not conn:
        print("DB 커넥션 실패")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW COLUMNS FROM pst_notice;")
            cols = cur.fetchall()
            print("[COLUMNS in pst_notice]:")
            for c in cols:
                print(c)
    except Exception as e:
        print("컬럼 조회 중 오류:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    check_notice_columns()
