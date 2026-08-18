import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_upload_login_required():
    client = app.test_client()

    # 1. 비로그인 상태로 PC /upload 접근 시 테스트
    with client:
        res = client.get('/upload', follow_redirects=False)
        print(f"비로그인 PC /upload GET status: {res.status_code}, redirect location: {res.headers.get('Location')}")
        assert res.status_code == 302, "비로그인 시 302 리다이렉트되어야 합니다!"
        assert 'open_login=true' in res.headers.get('Location', ''), "로그인 모달 파라미터가 포함되어야 합니다!"

    # 2. 비로그인 상태로 Mobile /m/upload 접근 시 테스트
    with client:
        res_m = client.get('/m/upload', follow_redirects=False)
        print(f"비로그인 Mobile /m/upload GET status: {res_m.status_code}, redirect location: {res_m.headers.get('Location')}")
        assert res_m.status_code == 302, "비로그인 시 302 리다이렉트되어야 합니다!"
        assert 'open_login=true' in res_m.headers.get('Location', ''), "로그인 모달 파라미터가 포함되어야 합니다!"

    # 3. 로그인 상태로 PC /upload 접근 시 테스트 (200 OK)
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_sns_user_999'

    res_logged_in = client.get('/upload', follow_redirects=False)
    print(f"로그인 상태 PC /upload GET status: {res_logged_in.status_code}")
    assert res_logged_in.status_code == 200, "로그인한 사용자는 200 OK로 페이지에 접근할 수 있어야 합니다!"

    print("\n[SUCCESS] 출전 등록 페이지(/upload, /m/upload) 로그인 미인증 차단 및 리다이렉트 검증 완수!")

if __name__ == '__main__':
    test_upload_login_required()
