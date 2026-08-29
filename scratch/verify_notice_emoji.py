import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.contest_service import service

def verify_emoji():
    conn = service.get_db_connection()
    if not conn:
        print("DB 커넥션 실패")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")
            cur.execute("SELECT NOTICE_NO, TTL, TTL_M FROM PST_NOTICE WHERE NOTICE_NO = 1;")
            row = cur.fetchone()
            print("[PST_NOTICE VERIFY]:")
            print(" TTL   :", row.get('TTL'))
            print(" TTL_M :", row.get('TTL_M'))
            
            cur.execute("SELECT NOTICE_NO, TTL, TTL_M FROM pst_notice WHERE NOTICE_NO = 1;")
            row2 = cur.fetchone()
            print("[pst_notice VERIFY]:")
            print(" TTL   :", row2.get('TTL'))
            print(" TTL_M :", row2.get('TTL_M'))
    except Exception as e:
        print("검증 오류:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    verify_emoji()
