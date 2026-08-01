import sys
sys.path.append('d:/dev/workspace1/pawstar')
from services.contest_service import service

def sync_db_counts():
    conn = service.get_db_connection()
    if not conn:
        print("DB 연결 실패")
        return

    try:
        with conn.cursor() as cur:
            # 1. 실제 pst_contest_vw 카운트 동기화
            cur.execute("""
                UPDATE pst_contest_round r
                SET VW_CNT = (
                    SELECT COUNT(*) FROM pst_contest_vw v
                    WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ENT_USER_ID = r.ENT_USER_ID
                );
            """)

            # 2. 실제 pst_contest_like 카운트 동기화
            cur.execute("""
                UPDATE pst_contest_round r
                SET LIKE_CNT = (
                    SELECT COUNT(*) FROM pst_contest_like l
                    WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ENT_USER_ID = r.ENT_USER_ID
                );
            """)

            # 3. 실제 pst_contest_cmt 카운트 동기화
            cur.execute("""
                UPDATE pst_contest_round r
                SET CMT_CNT = (
                    SELECT COUNT(*) FROM pst_contest_cmt c
                    WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ENT_USER_ID = r.ENT_USER_ID
                );
            """)

            # 4. 종합 점수 SCORE 보정 계산 (SCORE = VW_CNT*1 + LIKE_CNT*5 + CMT_CNT*10)
            cur.execute("""
                UPDATE pst_contest_round
                SET SCORE = (VW_CNT * 1) + (LIKE_CNT * 5) + (CMT_CNT * 10);
            """)

            conn.commit()
            print("=== DB COUNT & SCORE SYNC SUCCESSFUL ===")
    except Exception as e:
        print("Sync Error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    sync_db_counts()
