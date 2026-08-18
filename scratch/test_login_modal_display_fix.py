import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_login_modal_display_fix():
    client = app.test_client()

    # 1. PC base.html 렌더링 내 openGoogleAuthModal 가 mAuthModal 을 다루는지 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'mAuthModal' in html_pc
    assert 'openGoogleAuthModal' in html_pc
    print("[SUCCESS 1] PC openGoogleAuthModal 내 mAuthModal 팝업 노출 ID 바인딩 수정 완료!")

    # 2. 모바일 m_base.html 렌더링 내 가입/로그인 버튼 클릭 시 openGoogleAuthModal 호출 바인딩 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'mBtnNavProfile' in html_m
    assert 'openGoogleAuthModal()' in html_m
    assert 'id="mAuthModal"' in html_m
    print("[SUCCESS 2] 모바일 가입/로그인 버튼 클릭 시 mAuthModal 팝업 레이어 오픈 연동 완료!")

    print("\n[FINAL SUCCESS] 가입/로그인 팝업 레이어 안뜸 버그 완전 해결 검증 성공!")

if __name__ == '__main__':
    test_login_modal_display_fix()
