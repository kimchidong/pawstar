import os
import sys
import importlib.util
import pymysql

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.web.py')
spec = importlib.util.spec_from_file_location("config_web", config_path)
config_web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_web)

DB_CONFIG = config_web.DB_CONFIG

def check_all_tables():
    conn = pymysql.connect(
        host=DB_CONFIG.get('host', 'localhost'),
        user=DB_CONFIG.get('user', 'root'),
        password=DB_CONFIG.get('password', ''),
        db=DB_CONFIG.get('db') or DB_CONFIG.get('database'),
        port=DB_CONFIG.get('port', 3306),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cur.fetchall()]

            for t in tables:
                cur.execute(f"DESCRIBE {t};")
                text_cols = [r['Field'] for r in cur.fetchall() if 'char' in r['Type'].lower() or 'text' in r['Type'].lower()]
                for col in text_cols:
                    cur.execute(f"SELECT COUNT(*) as count FROM {t} WHERE {col} LIKE '%/static/image/paw/%';")
                    cnt = cur.fetchone()['count']
                    if cnt > 0:
                        print(f"Found {cnt} rows in {t}.{col} matching '/static/image/paw/'")
                        cur.execute(f"""
                            UPDATE {t}
                            SET {col} = REPLACE({col}, '/static/image/paw/', '/static/image/contest/')
                            WHERE {col} LIKE '%/static/image/paw/%';
                        """)
                        print(f"Updated {t}.{col}: {cur.rowcount} rows affected.")
            conn.commit()
            print("=== Full Database Check & Migration Finished ===")
    except Exception as e:
        print("Error during full DB check:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    check_all_tables()
