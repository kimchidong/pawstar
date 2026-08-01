import sys
import uuid
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def fix_file_format_with_random_uuid():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CONTEST_ROUND, ENT_USER_ID FROM pst_contest_round;")
            rows = cur.fetchall()

            for r in rows:
                c_id = r['CONTEST_ROUND']
                u_id = r['ENT_USER_ID']
                random_uuid = uuid.uuid4().hex[:12]
                f1 = f"{c_id}_{random_uuid}_1.webp"
                f2 = f"{c_id}_{random_uuid}_2.webp"

                cur.execute("""
                    UPDATE pst_contest_round
                    SET PHT_FILE1 = %s, PHT_FILE2 = %s
                    WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                """, (f1, f2, c_id, u_id))

            conn.commit()
            print("=== DB PHT_FILE1 & PHT_FILE2 RANDOM UUID UPDATE SUCCESS ===")
    except Exception as e:
        print("Fix format error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_file_format_with_random_uuid()
