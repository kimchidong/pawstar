import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from services.contest_service import PawStarService

def test_contest_round_sns():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB connection failed!")
        sys.exit(1)

    print("Checking PST_CONTEST_ROUND columns...")
    with conn.cursor() as cur:
        for col in ['SNS_INST', 'SNS_YTB', 'SNS_FSB', 'SNS_BLG']:
            cur.execute(f"SHOW COLUMNS FROM PST_CONTEST_ROUND LIKE '{col}'")
            row = cur.fetchone()
            if row:
                print(f"Column {col} exists: {row}")
            else:
                print(f"Column {col} DOES NOT EXIST!")

    print("Testing create_contest_entry with SNS links...")
    test_user = "test_sns_user_999"
    test_inst = "https://instagram.com/test_entry_inst"
    test_ytb = "https://youtube.com/@test_entry_ytb"
    test_fsb = "https://facebook.com/test_entry_fsb"
    test_blg = "https://blog.naver.com/test_entry_blg"

    curr = service.get_current_contest()
    c_id = curr.get('CONTEST_ROUND', 1) if curr else 1

    res = service.create_contest_entry(
        contest_id=c_id,
        user_id=test_user,
        kind_cd="K001",
        pet_name="SNS테스트펫",
        title="SNS 출전 테스트",
        content="SNS 출전 내용",
        file_path1="/static/image/test.jpg",
        file_path2="/static/image/test.jpg",
        sns_inst=test_inst,
        sns_ytb=test_ytb,
        sns_fsb=test_fsb,
        sns_blg=test_blg
    )
    print("Entry creation result:", res)
    assert res.get('success') == True, "Failed to create entry"

    round_no = res['round_no']
    print(f"Verifying stored SNS data for contest {c_id}, round_no {round_no}...")

    conn2 = service.get_db_connection()
    with conn2.cursor() as cur:
        cur.execute("""
            SELECT SNS_INST, SNS_YTB, SNS_FSB, SNS_BLG
            FROM PST_CONTEST_ROUND
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (c_id, round_no))
        saved = cur.fetchone()
        print("Saved DB row:", saved)
        assert saved['SNS_INST'] == test_inst, f"INST mismatch: {saved['SNS_INST']}"
        assert saved['SNS_YTB'] == test_ytb, f"YTB mismatch: {saved['SNS_YTB']}"
        assert saved['SNS_FSB'] == test_fsb, f"FSB mismatch: {saved['SNS_FSB']}"
        assert saved['SNS_BLG'] == test_blg, f"BLG mismatch: {saved['SNS_BLG']}"

    print("Verifying get_user_profile API returns PST_CONTEST_ROUND SNS values...")
    user_data = service.get_user_profile(test_user, contest_id=c_id)
    posts = user_data.get('my_posts', [])
    assert len(posts) > 0, "No posts returned for test user"
    target_post = posts[0]
    print("Fetched post SNS_INST:", target_post.get('SNS_INST'), "sns_inst:", target_post.get('sns_inst'))
    assert target_post.get('SNS_INST') == test_inst
    assert target_post.get('sns_inst') == test_inst

    # Clean up test entry
    with conn2.cursor() as cur:
        cur.execute("DELETE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s", (c_id, test_user))
        conn2.commit()
    conn2.close()

    print("ALL PST_CONTEST_ROUND SNS TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_contest_round_sns()
