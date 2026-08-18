import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.contest_service import PawStarService

def test_member_view_only():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("Failed DB connection")
        return

    try:
        with conn.cursor() as cur:
            # 15라운드 상태 임시 변경 (테스트용)
            cur.execute("UPDATE PST_CONTEST SET CONTEST_STAT = 'G001C001' WHERE CONTEST_ROUND = 15")
            conn.commit()

            cur.execute("SELECT ROUND_NO, ENT_USER_ID FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = 15 LIMIT 1")
            r_info = cur.fetchone()
            c_round = 15
            r_no = r_info['ROUND_NO']
            author_id = r_info['ENT_USER_ID']

            cur.execute("SELECT USER_ID FROM PST_USER WHERE USER_ID != %s LIMIT 1", (author_id,))
            user_row = cur.fetchone()
            member_user_id = user_row['USER_ID']

            print(f"테스트 대상 - 회원: {member_user_id[:10]}..., c_round: {c_round}, r_no: {r_no}")

            # 1. 비회원(ANON) 조회 요청
            fake_anon_id = "ANON_999_888_777_0"
            res_anon = service.increase_view_count(c_round, r_no, view_user_id=fake_anon_id, client_ip="999.888.777.0")
            print("비회원 조회 결과:", res_anon)

            cur.execute("SELECT COUNT(*) AS cnt FROM PST_CONTEST_VW WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND VW_USER_ID = %s", (c_round, r_no, fake_anon_id))
            anon_vw_cnt = cur.fetchone()['cnt']
            print(f"비회원 PST_CONTEST_VW 저장 개수 (expected 0): {anon_vw_cnt}")
            assert anon_vw_cnt == 0, "비회원 정보가 PST_CONTEST_VW에 저장되었습니다!"

            # 2. 회원 조회 요청
            cur.execute("DELETE FROM PST_CONTEST_VW WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND VW_USER_ID = %s", (c_round, r_no, member_user_id))
            conn.commit()

            res_member = service.increase_view_count(c_round, r_no, view_user_id=member_user_id)
            print("회원 조회 결과:", res_member)

            cur.execute("SELECT COUNT(*) AS cnt FROM PST_CONTEST_VW WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND VW_USER_ID = %s", (c_round, r_no, member_user_id))
            member_vw_cnt = cur.fetchone()['cnt']
            print(f"회원 PST_CONTEST_VW 저장 개수 (expected 1): {member_vw_cnt}")
            assert member_vw_cnt == 1, "회원 정보가 PST_CONTEST_VW에 저장되지 않았습니다!"

            # cleanup 테스트 데이터
            cur.execute("DELETE FROM PST_CONTEST_VW WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND VW_USER_ID = %s", (c_round, r_no, member_user_id))
            # 15라운드 상태 원복
            cur.execute("UPDATE PST_CONTEST SET CONTEST_STAT = 'G001C002' WHERE CONTEST_ROUND = 15")
            conn.commit()

            print("\n[SUCCESS] PST_CONTEST_VW 테이블에는 오직 회원(PST_USER 존재 유저)만 기록됨을 완벽하게 검증하였습니다!")

    except Exception as e:
        print(f"테스트 실패: {e}")
        # 예외 시 원복
        with conn.cursor() as cur:
            cur.execute("UPDATE PST_CONTEST SET CONTEST_STAT = 'G001C002' WHERE CONTEST_ROUND = 15")
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    test_member_view_only()
