import pymysql
import uuid
import os
import importlib.util

def _get_config_web():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.web.py'),
        os.path.join(curr_dir, '..', 'config.web.py'),
        os.path.join(os.getcwd(), 'config.web.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_web", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.web.py 파일을 찾을 수 없습니다.")

config_web = _get_config_web()
DB_CONFIG = config_web.DB_CONFIG

def migrate():
    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
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
