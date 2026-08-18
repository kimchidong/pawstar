import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_upload_login_popup():
    client = app.test_client()

    # 1. 비로그인 PC /upload 접근 시 login_notice 템플릿 렌더링 확인 (200 OK + 안내문구)
    with client:
        res_pc = client.get('/upload')
        print(f"PC /upload GET status: {res_pc.status_code}")
        assert res_pc.status_code == 200, "200 OK 상태로 안내 팝업 페이지가 표시되어야 합니다!"
        assert '로그인 필요' in res_pc.get_data(as_text=True), "안내 문구('로그인 필요')가 응답 HTML에 있어야 합니다!"
        assert '/auth/google' in res_pc.get_data(as_text=True), "구글 로그인 링크 경로가 있어야 합니다!"

    # 2. 비로그인 Mobile /m/upload 접근 시 login_notice 템플릿 렌더링 확인 (200 OK + 안내문구)
    with client:
        res_m = client.get('/m/upload')
        print(f"Mobile /m/upload GET status: {res_m.status_code}")
        assert res_m.status_code == 200, "200 OK 상태로 안내 팝업 페이지가 표시되어야 합니다!"
        assert '로그인 필요' in res_m.get_data(as_text=True), "안내 문구('로그인 필요')가 응답 HTML에 있어야 합니다!"

    print("\n[SUCCESS] 비로그인 출전 등록 페이지 접근 시 로그인 안내 팝업 노출 및 구글 로그인 연결 검증 성공!")

if __name__ == '__main__':
    test_upload_login_popup()
