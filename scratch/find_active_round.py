import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.contest_service import PawStarService

s = PawStarService()
conn = s.get_db_connection()
with conn.cursor() as cur:
    cur.execute("""
        SELECT r.CONTEST_ROUND, r.ROUND_NO, r.ENT_USER_ID, c.CONTEST_STAT
        FROM PST_CONTEST_ROUND r
        JOIN PST_CONTEST c ON r.CONTEST_ROUND = c.CONTEST_ROUND
    """)
    rows = cur.fetchall()
    for r in rows:
        print(r)
conn.close()
