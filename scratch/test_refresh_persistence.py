import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask import session

def test_refresh_persistence():
    client = app.test_client()

    # 1. 로그인 상태 설정
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True
            sess.pop('logged_out', None)

        res1 = client.get('/')
        print(f"[1] 로그인 직후 GET / -> 로그인 상태 포함 여부: {'로그아웃' in res1.get_data(as_text=True)}")
        assert '로그아웃' in res1.get_data(as_text=True)

        # 2. 로그아웃 수행
        res_logout = client.get('/logout', follow_redirects=False)
        print(f"[2] GET /logout -> Status: {res_logout.status_code}, Location: {res_logout.headers.get('Location')}")

        # 3. 첫 번째 메인 페이지 접근 (리다이렉트)
        res_first = client.get('/')
        has_login_btn_1 = '가입/로그인' in res_first.get_data(as_text=True)
        has_logout_btn_1 = '로그아웃' in res_first.get_data(as_text=True)
        print(f"[3] 로그아웃 직후 GET / -> 가입/로그인버튼: {has_login_btn_1}, 로그아웃버튼: {has_logout_btn_1}")
        assert has_login_btn_1 is True
        assert has_logout_btn_1 is False

        # 4. 새로고침 (두 번째 메인 페이지 접근)
        res_refresh1 = client.get('/')
        has_login_btn_2 = '가입/로그인' in res_refresh1.get_data(as_text=True)
        has_logout_btn_2 = '로그아웃' in res_refresh1.get_data(as_text=True)
        print(f"[4] 새로고침(1차) GET / -> 가입/로그인버튼: {has_login_btn_2}, 로그아웃버튼: {has_logout_btn_2}")
        assert has_login_btn_2 is True
        assert has_logout_btn_2 is False

        # 5. 새로고침 (세 번째 메인 페이지 접근)
        res_refresh2 = client.get('/')
        has_login_btn_3 = '가입/로그인' in res_refresh2.get_data(as_text=True)
        has_logout_btn_3 = '로그아웃' in res_refresh2.get_data(as_text=True)
        print(f"[5] 새로고침(2차) GET / -> 가입/로그인버튼: {has_login_btn_3}, 로그아웃버튼: {has_logout_btn_3}")
        assert has_login_btn_3 is True
        assert has_logout_btn_3 is False

        # 6. 모바일 새로고침 테스트 (/m)
        res_m_refresh = client.get('/m')
        has_m_login = '가입/로그인' in res_m_refresh.get_data(as_text=True)
        has_m_logout = '로그아웃' in res_m_refresh.get_data(as_text=True)
        print(f"[6] 모바일 새로고침 GET /m -> 가입/로그인버튼: {has_m_login}, 로그아웃버튼: {has_m_logout}")
        assert has_m_login is True

    print("\n[SUCCESS] 로그아웃 후 새로고침 시 로그인 상태가 되살아나지 않고 비로그인 상태가 영구히 명확하게 유지됨을 검증 완료!")

if __name__ == '__main__':
    test_refresh_persistence()
