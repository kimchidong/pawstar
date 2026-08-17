import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from services.contest_service import PawStarService

def test_db_save_assurance():
    service = PawStarService()
    conn = service.get_db_connection()
    assert conn is not None

    curr = service.get_current_contest()
    contest_id = (curr.get('CONTEST_ROUND') or curr.get('contest_id') or 1) if curr else 1
    print(f"Active contest ID: {contest_id}")

    # Case 1: user_id is None / empty string
    print("Testing create_contest_entry with user_id = None...")
    res = service.create_contest_entry(
        contest_id=contest_id,
        user_id=None,
        kind_cd="K001",
        pet_name="세션테스트펫",
        title="세션 비로그인 출전 테스트",
        content="내용 테스트",
        file_path1="/static/image/test1.webp",
        file_path2="/static/image/test2.webp"
    )
    print("Result for user_id=None:", res)
    assert res.get('success') == True, f"Failed for user_id=None: {res}"

    r_no = res['round_no']
    ent_user = res['ent_user_id']
    print(f"Checking DB record for round_no {r_no}, ent_user_id {ent_user}...")

    conn2 = service.get_db_connection()
    with conn2.cursor() as cur:
        cur.execute("""
            SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, PET_NM, TITLE
            FROM PST_CONTEST_ROUND
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (contest_id, r_no))
        row = cur.fetchone()
        print("DB Row:", row)
        assert row is not None, "DB ROW IS MISSING!"

        # Cleanup test row
        cur.execute("DELETE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (contest_id, r_no))
        conn2.commit()
    conn2.close()

    print("ALL DB SAVE ASSURANCE TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_db_save_assurance()
