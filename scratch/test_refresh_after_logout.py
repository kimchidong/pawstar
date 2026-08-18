import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask import session

def test_refresh_after_logout():
    client = app.test_client()

    # 1. 로그인 상태 가정
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True
            sess.pop('logged_out', None)

        print("[Step 1] 로그인 직후 GET / 접근")
        res1 = client.get('/')
        print(f"로그인 상태 / : is_logged_in in HTML? {'로그아웃' in res1.get_data(as_text=True)}")

        # 2. 로그아웃 수행
        print("\n[Step 2] GET /logout 호출")
        res_logout = client.get('/logout', follow_redirects=False)
        print(f"Logout status: {res_logout.status_code}, Location: {res_logout.headers.get('Location')}")
        print("Set-Cookie headers:", res_logout.headers.getlist('Set-Cookie'))

        # 3. 로그아웃 리다이렉트 이동 (첫 번째 GET /)
        print("\n[Step 3] 로그아웃 직후 리다이렉트 GET / 접근")
        res_redirect = client.get('/')
        has_logout_btn1 = '로그아웃' in res_redirect.get_data(as_text=True)
        has_login_btn1 = '가입/로그인' in res_redirect.get_data(as_text=True)
        print(f"로그아웃 직후 / -> 로그아웃버튼 존재?: {has_logout_btn1}, 가입/로그인버튼 존재?: {has_login_btn1}")

        # 4. 새로고침 (두 번째 GET /)
        print("\n[Step 4] 새로고침 GET / 접근 (두 번째 GET)")
        res_refresh = client.get('/')
        has_logout_btn2 = '로그아웃' in res_refresh.get_data(as_text=True)
        has_login_btn2 = '가입/로그인' in res_refresh.get_data(as_text=True)
        print(f"새로고침 후 / -> 로그아웃버튼 존재?: {has_logout_btn2}, 가입/로그인버튼 존재?: {has_login_btn2}")
        print(f"새로고침 후 session.get('user_id'): {session.get('user_id')}")

if __name__ == '__main__':
    test_refresh_after_logout()
