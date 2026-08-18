import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_upload_google_redirect():
    client = app.test_client()

    # 1. PC /upload 접근 시 /auth/google?next=/upload 리다이렉트 확인
    with client:
        res_pc = client.get('/upload', follow_redirects=False)
        print(f"PC /upload status: {res_pc.status_code}, location: {res_pc.headers.get('Location')}")
        assert res_pc.status_code == 302
        assert '/auth/google?next=%2Fupload' in res_pc.headers.get('Location') or '/auth/google?next=/upload' in res_pc.headers.get('Location')

    # 2. Mobile /m/upload 접근 시 /auth/google?next=/m/upload 리다이렉트 확인
    with client:
        res_m = client.get('/m/upload', follow_redirects=False)
        print(f"Mobile /m/upload status: {res_m.status_code}, location: {res_m.headers.get('Location')}")
        assert res_m.status_code == 302
        assert '/auth/google?next=%2Fm%2Fupload' in res_m.headers.get('Location') or '/auth/google?next=/m/upload' in res_m.headers.get('Location')

    print("\n[SUCCESS] 비로그인 상태에서 출전등록 페이지 접근 시 구글 로그인 페이지로 리다이렉트 처리 검증 완료!")

if __name__ == '__main__':
    test_upload_google_redirect()
