import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.contest_service import service

def check_tables():
    conn = service.get_db_connection()
    if not conn:
        print("DB 커넥션 실패")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = [list(t.values())[0] for t in cur.fetchall()]
            print("[EXISTING TABLES IN DB]:")
            for t in tables:
                if 'notice' in t.lower():
                    print(" -> NOTICE TABLE:", t)
                else:
                    print(" -", t)
    except Exception as e:
        print("테이블 조회 오류:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    check_tables()
