import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.contest_service import service

def check_stat():
    conn = service.get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM PST_CONTEST")
            rows = cur.fetchall()
            print("PST_CONTEST rows:", rows)
        conn.close()

if __name__ == '__main__':
    check_stat()
