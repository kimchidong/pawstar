import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask import session

def test_m_logout_complete():
    client = app.test_client()

    # 1. 모바일 로그인 상태로 GET /m/logout 호출 테스트
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_sns_user_999'
            sess['is_logged_in'] = True

        # 모바일 로그아웃 요청
        res = client.get('/m/logout', follow_redirects=False)
        print(f"GET /m/logout status: {res.status_code}, redirect: {res.headers.get('Location')}")
        assert res.status_code == 302, "302 리다이렉트가 반환되어야 합니다."
        assert res.headers.get('Location') == '/m', "모바일 메인 페이지(/m)로 리다이렉트되어야 합니다."
        assert session.get('user_id') is None, "세션의 user_id가 삭제되어야 합니다."
        assert session.get('logged_out') is True, "logged_out 상태가 설정되어야 합니다."

    # 2. 로그아웃 후 모바일 메인피드 GET /m 접근 시 비로그인 렌더링 검증
    with client:
        res_m_index = client.get('/m')
        print(f"GET /m status: {res_m_index.status_code}")
        assert res_m_index.status_code == 200
        assert '가입/로그인' in res_m_index.get_data(as_text=True), "로그아웃 후 비로그인(가입/로그인) 상태로 렌더링되어야 합니다."

    print("\n[SUCCESS] 모바일 환경에서의 완벽한 로그아웃/쿠키/세션 파기 및 UI 최신화 검증 완료!")

if __name__ == '__main__':
    test_m_logout_complete()
