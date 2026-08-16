import sys
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def fix_db_pht_paths():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            # 1. PHT_PATH가 1-1.webp 처럼 파일명으로 저장된 건들을 규격 경로로 교정
            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_PATH = '/static/image/contest/2026/08/',
                    PHT_FILE1 = '1-1_1.webp',
                    PHT_FILE2 = '1-1_2.webp'
                WHERE PHT_PATH NOT LIKE '/%' OR PHT_PATH LIKE '%.webp%' OR PHT_PATH LIKE '%.jpg%';
            """)

            # 2. PHT_FILE2가 비어있는 경우 PHT_FILE1으로 채움
            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_FILE2 = PHT_FILE1
                WHERE PHT_FILE2 IS NULL OR PHT_FILE2 = '';
            """)

            # 3. PHT_PATH 끝에 / 가 없는 경우 붙여주기
            cur.execute("""
                UPDATE pst_contest_round
                SET PHT_PATH = CONCAT(PHT_PATH, '/')
                WHERE PHT_PATH LIKE '/%' AND PHT_PATH NOT LIKE '%/';
            """)

            conn.commit()
            print("=== DB PHT_PATH / PHT_FILE1 / PHT_FILE2 MIGRATION COMPLETE ===")
    except Exception as e:
        print("Fix PHT error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_db_pht_paths()
