import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.contest_service import PawStarService

s = PawStarService()
conn = s.get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT CONTEST_ROUND, CONTEST_STAT FROM PST_CONTEST")
    print(cur.fetchall())
conn.close()
