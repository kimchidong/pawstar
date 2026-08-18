import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.contest_service import PawStarService

def clean_non_member_views():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("Failed to connect DB")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM PST_CONTEST_VW
                WHERE VW_USER_ID NOT IN (SELECT USER_ID FROM PST_USER) OR VW_USER_ID LIKE 'ANON_%%'
            """)
            invalid_cnt = cur.fetchone()['cnt']
            print(f"PST_USER에 없는 비회원 조회수 레코드 수: {invalid_cnt}")

            if invalid_cnt > 0:
                cur.execute("""
                    DELETE FROM PST_CONTEST_VW
                    WHERE VW_USER_ID NOT IN (SELECT USER_ID FROM PST_USER) OR VW_USER_ID LIKE 'ANON_%%'
                """)
                deleted_rows = cur.rowcount
                conn.commit()
                print(f"삭제 완료된 비회원 조회수 레코드 수: {deleted_rows}")
            else:
                print("삭제할 비회원 레코드가 없습니다.")

            cur.execute("SELECT DISTINCT CONTEST_ROUND, ROUND_NO FROM PST_CONTEST_ROUND")
            rounds = cur.fetchall()
            for r in rounds:
                service.sync_and_get_post_stats(cur, r['CONTEST_ROUND'], r['ROUND_NO'])
            conn.commit()
            print("모든 콘테스트 출전글 통계 재동기화 완료")

    except Exception as e:
        print(f"Error clean_non_member_views: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    clean_non_member_views()
