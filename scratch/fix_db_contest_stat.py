import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.contest_service import service

def fix_contest_stat():
    conn = service.get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # 1. 1회차 CONTEST_STAT를 'G001C001'(진행중)으로 업데이트
            cur.execute("""
                UPDATE PST_CONTEST
                SET CONTEST_STAT = 'G001C001'
                WHERE CONTEST_ROUND = 1
            """)
            conn.commit()
            print("[SUCCESS] PST_CONTEST CONTEST_ROUND = 1 상태를 G001C001(진행중)으로 업데이트 완료!")

            # 확인 조회
            cur.execute("SELECT CONTEST_ROUND, CONTEST_STAT FROM PST_CONTEST WHERE CONTEST_ROUND = 1")
            row = cur.fetchone()
            print("Updated Row:", row)
        conn.close()

if __name__ == '__main__':
    fix_contest_stat()
