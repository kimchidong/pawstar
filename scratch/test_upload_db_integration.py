import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from services.contest_service import PawStarService

def test_upload_db_integration():
    service = PawStarService()
    conn = service.get_db_connection()
    assert conn is not None, "DB connection failed!"

    curr = service.get_current_contest()
    contest_id = (curr.get('CONTEST_ROUND') or curr.get('contest_id') or 1) if curr else 1
    print(f"Current contest ID: {contest_id}")

    test_user = "integration_test_user_777"
    pet_name = "초코"
    pet_type = "🐕 강아지"
    title = "DB 저장 통합 테스트 제목"
    content = "DB 저장 통합 테스트 내용입니다."
    path1 = "/static/image/temp/test_1.webp"
    path2 = "/static/image/temp/test_2.webp"
    sns_inst = "https://instagram.com/choco_test"
    sns_ytb = "https://youtube.com/@choco_test"
    sns_fsb = "https://facebook.com/choco_test"
    sns_blg = "https://blog.naver.com/choco_test"

    print("Creating post via service.create_post...")
    res = service.create_post(
        contest_id=contest_id,
        user_id=test_user,
        pet_name=pet_name,
        pet_type=pet_type,
        title=title,
        content=content,
        file_path1=path1,
        file_path2=path2,
        sns_inst=sns_inst,
        sns_ytb=sns_ytb,
        sns_fsb=sns_fsb,
        sns_blg=sns_blg
    )

    print("create_post return result:", res)
    assert res.get('success') == True, f"create_post failed: {res}"

    round_no = res.get('ROUND_NO') or res.get('round_no')
    print(f"Verifying DB record for CONTEST_ROUND={contest_id}, ROUND_NO={round_no}...")

    conn2 = service.get_db_connection()
    with conn2.cursor() as cur:
        cur.execute("""
            SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, PET_NM, TITLE, CONTS, PHT_FILE_PATH1, PHT_FILE_PATH2, SNS_INST, SNS_YTB, SNS_FSB, SNS_BLG
            FROM PST_CONTEST_ROUND
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (contest_id, round_no))
        row = cur.fetchone()
        print("DB Row found:", row)
        assert row is not None, "DB ROW NOT FOUND IN PST_CONTEST_ROUND!"
        assert row['ENT_USER_ID'] == test_user
        assert row['PET_NM'] == pet_name
        assert row['TITLE'] == title
        assert row['CONTS'] == content
        assert row['PHT_FILE_PATH1'] == path1
        assert row['SNS_INST'] == sns_inst
        assert row['SNS_YTB'] == sns_ytb

        # Clean up
        cur.execute("DELETE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s", (contest_id, test_user))
        conn2.commit()
    conn2.close()

    print("INTEGRATION DB TEST PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_upload_db_integration()
