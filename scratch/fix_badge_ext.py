import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.contest_service import service

def fix_badge_extensions():
    conn = service.get_db_connection()
    if not conn:
        print("DB connection failed")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE pst_award SET BADGE_IMG_PATH_FILE = REPLACE(BADGE_IMG_PATH_FILE, '.webp', '.png')")
            conn.commit()
            cur.execute("SELECT AWARD_CD, AWARD_NM, BADGE_IMG_PATH_FILE FROM pst_award")
            rows = cur.fetchall()
            print("Updated pst_award rows:")
            for r in rows:
                print(r)
        conn.close()
    except Exception as e:
        print("Error updating pst_award:", e)

if __name__ == "__main__":
    fix_badge_extensions()
