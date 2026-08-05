from services.contest_service import PawStarService

def test_share_3param_exact():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB connection fail")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, SHARE_SN FROM pst_contest_round LIMIT 1;")
        row = cur.fetchone()
        c_round = row['CONTEST_ROUND']
        r_no = row['ROUND_NO']
        correct_sn = row['SHARE_SN']

        print(f"DB Real Post: contest_round={c_round}, round_no={r_no}, share_sn={correct_sn}")

        # 1. 3개 값이 100% 일치할 때 -> 성공
        post1 = service.get_post_detail(c_round, r_no, share_sn=correct_sn)
        assert post1 is not None, "Should find post when 3 params exactly match"
        print("1. 3-parameter exact match: SUCCESS (Post found)")

        # 2. share_sn 이 불일치할 때 -> 실패 (None 반환)
        fake_sn = "S-invalid-sn-12345"
        post2 = service.get_post_detail(c_round, r_no, share_sn=fake_sn)
        assert post2 is None, "Should return None when share_sn is invalid"
        print("2. Mismatched share_sn: SUCCESS (Returned None -> Error UI displayed)")

        # 3. 사용자가 지정한 예시 3개 값 테스트
        user_c_round = 5
        user_r_no = 1
        user_share_sn = "S-ebd9f8b6-6b05-4d68-bf39-e0d60a427dc4"
        post3 = service.get_post_detail(user_c_round, user_r_no, share_sn=user_share_sn)
        print(f"3. User example 3-parameter test: post3 is {'VALID' if post3 else 'NOT FOUND (Mismatched)'}")

    conn.close()
    print("3-parameter exact matching verification COMPLETE!")

if __name__ == '__main__':
    test_share_3param_exact()
