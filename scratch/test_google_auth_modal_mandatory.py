import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_google_auth_modal_mandatory():
    client = app.test_client()

    # 1. 비로그인 PC 상태에서 /upload 접근 시 open_login=true 와 함께 / 메인피드로 302 리다이렉트 되는지 검증
    res_pc_upload = client.get('/upload', follow_redirects=False)
    print(f"GET /upload status: {res_pc_upload.status_code}, redirect: {res_pc_upload.headers.get('Location')}")
    assert res_pc_upload.status_code == 302
    assert 'open_login=true' in res_pc_upload.headers.get('Location')
    print("[SUCCESS 1] PC 비로그인 출전페이지 접근 시 open_login=true 모달 오프너 리다이렉트 완수!")

    # 2. 비로그인 모바일 상태에서 /m/upload 접근 시 open_login=true 와 함께 /m 메인피드로 302 리다이렉트 되는지 검증
    res_m_upload = client.get('/m/upload', follow_redirects=False)
    print(f"GET /m/upload status: {res_m_upload.status_code}, redirect: {res_m_upload.headers.get('Location')}")
    assert res_m_upload.status_code == 302
    assert 'open_login=true' in res_m_upload.headers.get('Location')
    print("[SUCCESS 2] 모바일 비로그인 출전페이지 접근 시 open_login=true 모달 오프너 리다이렉트 완수!")

    # 3. /?open_login=true 접근 시 HTML 내 googleAuthModal 및 openGoogleAuthModal() 바인딩 검증
    res_pc_main = client.get('/?open_login=true')
    html_pc = res_pc_main.get_data(as_text=True)
    assert 'id="googleAuthModal"' in html_pc
    assert 'openGoogleAuthModal()' in html_pc
    assert 'Google 계정 인증' in html_pc
    print("[SUCCESS 3] PC 메인 피드 상에서 사진 속 Google 계정 인증 모달 팝업 레이어 탑재 확인!")

    # 4. /m/?open_login=true 접근 시 HTML 내 googleAuthModal 및 openGoogleAuthModal() 바인딩 검증
    res_m_main = client.get('/m/?open_login=true')
    html_m = res_m_main.get_data(as_text=True)
    assert 'id="googleAuthModal"' in html_m
    assert 'openGoogleAuthModal()' in html_m
    assert 'Google 계정 인증' in html_m
    print("[SUCCESS 4] 모바일 메인 피드 상에서 사진 속 Google 계정 인증 모달 팝업 레이어 탑재 확인!")

    print("\n[FINAL SUCCESS] 모바일/PC 불문 로그인 필요 페이지 접근 시 Google 계정 인증 모달 팝업 강제 노출 검증 완료!")

if __name__ == '__main__':
    test_google_auth_modal_mandatory()
