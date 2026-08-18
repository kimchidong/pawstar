import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_remove_top_header_logout():
    client = app.test_client()

    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        res = client.get('/')
        html = res.get_data(as_text=True)

        assert 'id="btnNavLogout"' not in html
        assert '로그아웃' not in html or 'btnNavLogout' not in html
        print("[SUCCESS] PC 상단 헤더 우측 로그아웃 버튼 삭제 완료!")

if __name__ == '__main__':
    test_remove_top_header_logout()
