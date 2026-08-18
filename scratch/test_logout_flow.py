import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask import session

def test_logout_flow():
    client = app.test_client()

    # 1. PC 로그아웃 테스트
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user_123'
            sess['is_logged_in'] = True

        res_logout_pc = client.get('/logout', follow_redirects=False)
        print(f"PC /logout GET status: {res_logout_pc.status_code}, redirect location: {res_logout_pc.headers.get('Location')}")
        assert res_logout_pc.status_code == 302
        assert res_logout_pc.headers.get('Location') == '/'
        assert session.get('user_id') is None
        assert session.get('logged_out') is True
        print("PC 로그아웃 세션 파기 검증 성공!")

    # 2. 모바일 로그아웃 테스트
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user_123'
            sess['is_logged_in'] = True

        res_logout_m = client.get('/m/logout', follow_redirects=False)
        print(f"Mobile /m/logout GET status: {res_logout_m.status_code}, redirect location: {res_logout_m.headers.get('Location')}")
        assert res_logout_m.status_code == 302
        assert res_logout_m.headers.get('Location') == '/m'
        assert session.get('user_id') is None
        assert session.get('logged_out') is True
        print("모바일 로그아웃 세션 파기 및 /m 리다이렉트 검증 성공!")

    print("\n[SUCCESS] 로그아웃 라우트 세션 및 쿠키 파기 검증 완료!")

if __name__ == '__main__':
    test_logout_flow()
