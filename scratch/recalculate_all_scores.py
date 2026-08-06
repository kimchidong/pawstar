import sys
import pymysql
sys.path.insert(0, '.')

from services.contest_service import PawStarService

def recalculate_all_scores():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection failed")
        return

    try:
        with conn.cursor() as cur:
            # 1. 모든 pst_contest_round 게시글 조회
            cur.execute("""
                SELECT 
                    r.CONTEST_ROUND, 
                    r.ROUND_NO, 
                    r.ENT_USER_ID, 
                    COALESCE(r.VW_CNT, 0) AS VW_CNT, 
                    COALESCE(r.LIKE_CNT, 0) AS LIKE_CNT, 
                    COALESCE(r.CMT_CNT, 0) AS CMT_CNT, 
                    COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT, 
                    COALESCE(r.SCORE, 0) AS OLD_SCORE
                FROM pst_contest_round r
            """)
            posts = cur.fetchall()

            print(f"[RECALCULATE SCORES] Total {len(posts)} posts found. Starting recalculation...")
            updated_count = 0

            for p in posts:
                c_round = p['CONTEST_ROUND']
                r_no = p['ROUND_NO']

                # 실제 이력 테이블 개수 재조회 (존재하는 경우)
                cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_vw WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                vw_cnt = cur.fetchone()['cnt']

                cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_like WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                like_cnt = cur.fetchone()['cnt']

                cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_cmt WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                cmt_cnt = cur.fetchone()['cnt']

                cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_share WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                share_record_cnt = cur.fetchone()['cnt']

                final_vw = max(vw_cnt, p['VW_CNT'])
                final_like = max(like_cnt, p['LIKE_CNT'])
                final_cmt = max(cmt_cnt, p['CMT_CNT'])
                final_share = max(share_record_cnt, p['SHARE_CNT'])

                new_score = (final_vw * 1) + (final_like * 5) + (final_cmt * 10) + (final_share * 10)

                cur.execute("""
                    UPDATE pst_contest_round
                    SET VW_CNT = %s, LIKE_CNT = %s, CMT_CNT = %s, SHARE_CNT = %s, SCORE = %s
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (final_vw, final_like, final_cmt, final_share, new_score, c_round, r_no))

                print(f"Post [{c_round}-{r_no}] ({p['ENT_USER_ID']}): VW={final_vw}, LIKE={final_like}, CMT={final_cmt}, SHARE={final_share} | Old Score: {p['OLD_SCORE']} -> New Score: {new_score}")
                updated_count += 1

            conn.commit()
            print(f"\n[RECALCULATE COMPLETE] Successfully updated {updated_count} posts!")
    finally:
        conn.close()

if __name__ == '__main__':
    recalculate_all_scores()
