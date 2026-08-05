import uuid
from services.contest_service import PawStarService

def test_share_10pt():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Fail")
        return

    c_round = 1
    r_no = 1
    new_user_id = f"share_10pt_user_{uuid.uuid4().hex[:6]}"

    with conn.cursor() as cur:
        # SHARE_SN 가져오기
        cur.execute("SELECT SHARE_SN FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s;", (c_round, r_no))
        row = cur.fetchone()
        share_sn = row['SHARE_SN']

        # 이전 상태 점수 조회
        prev_detail = service.get_post_detail(c_round, r_no)
        prev_score = prev_detail.get('score') or prev_detail.get('SCORE') or 0
        prev_share = prev_detail.get('share_count') or prev_detail.get('SHARE_CNT') or 0

        # 공유 가입 진행 (+10점 추가 적립)
        res = service.increment_share_count_on_signup(c_round, r_no, share_sn, user_id=new_user_id)
        assert res is True, "increment_share_count_on_signup failed"

        # 새로운 상태 점수 조회
        after_detail = service.get_post_detail(c_round, r_no)
        after_score = after_detail.get('score') or after_detail.get('SCORE') or 0
        after_share = after_detail.get('share_count') or after_detail.get('SHARE_CNT') or 0

        print(f"Prev Share: {prev_share}, After Share: {after_share}")
        print(f"Prev Score: {prev_score}, After Score: {after_score}")

        # 공유 횟수는 +1 증가, 점수(SCORE)는 정확히 +10점 증가해야 함!
        assert after_share == prev_share + 1, "share_count should increment by 1"
        assert after_score == prev_score + 10, f"score should increment by 10, expected {prev_score + 10}, got {after_score}"
        print("Share signup +10pt verification SUCCESS!")

    conn.close()

if __name__ == '__main__':
    test_share_10pt()
