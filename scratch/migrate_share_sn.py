import pymysql
import uuid
from config import db_config

def migrate():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, SHARE_SN FROM pst_contest_round;")
        rows = cur.fetchall()
        updated_cnt = 0
        for r in rows:
            c_round = r['CONTEST_ROUND']
            r_no = r['ROUND_NO']
            sn = r.get('SHARE_SN')
            if not sn:
                new_sn = f"S-{uuid.uuid4()}"
            elif not sn.startswith('S-'):
                new_sn = f"S-{sn}"
            else:
                continue

            cur.execute("UPDATE pst_contest_round SET SHARE_SN = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s;", (new_sn, c_round, r_no))
            updated_cnt += 1

        conn.commit()
        print(f"Migrated {updated_cnt} records with S- prefix SHARE_SN!")
    conn.close()

if __name__ == '__main__':
    migrate()
