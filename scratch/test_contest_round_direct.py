import os
import sys
import io
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from app import app, service

def test_api_create_post_round():
    client = app.test_client()
    curr = service.get_current_contest()
    active_cid = curr.get('CONTEST_ROUND')
    print(f"Current Active Contest Round in DB: {active_cid}")

    dummy_image = (io.BytesIO(b"fake image bytes"), 'test_pet.jpg')

    # Simulate mobile/web form submission via API
    res = client.post('/api/post/create', data={
        'pet_name': '초코볼',
        'pet_type': '🐕 강아지',
        'title': '회차 키 바인딩 검증 출전',
        'content': '13회차 저장 정상 여부 디버깅',
        'media_file': dummy_image,
        'sns_inst': 'https://instagram.com/chocoball',
        'sns_ytb': 'https://youtube.com/@chocoball',
        'sns_fsb': '',
        'sns_blg': ''
    }, content_type='multipart/form-data')

    print("API Response status:", res.status_code)
    print("API Response json:", res.get_json())
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data.get('success') == True

    post_info = res_data.get('post', {})
    saved_round = post_info.get('CONTEST_ROUND') or post_info.get('contest_id')
    saved_round_no = post_info.get('ROUND_NO') or post_info.get('round_no')
    print(f"Saved post CONTEST_ROUND: {saved_round}, ROUND_NO: {saved_round_no}")
    assert saved_round == active_cid, f"Expected {active_cid}, but got {saved_round}"

    # Check DB directly
    conn = service.get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT CONTEST_ROUND, ROUND_NO, PET_NM, TITLE, SNS_INST, SNS_YTB
            FROM PST_CONTEST_ROUND
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (saved_round, saved_round_no))
        db_row = cur.fetchone()
        print("DB Row found:", db_row)
        assert db_row is not None
        assert db_row['CONTEST_ROUND'] == active_cid
        assert db_row['SNS_INST'] == 'https://instagram.com/chocoball'

        # Cleanup
        cur.execute("DELETE FROM PST_CONTEST_ROUND WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (saved_round, saved_round_no))
        conn.commit()
    conn.close()

    print("ROUND BINDING INTEGRATION TEST PASSED PERFECTLY!")

if __name__ == '__main__':
    test_api_create_post_round()
