import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_terms_privacy_popup_layer():
    client = app.test_client()

    # 1. base.html PC 메인 페이지 렌더링 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert "modal.style.zIndex = '2000000'" in html_pc
    assert 'openTermsNoticeModal()' in html_pc
    assert 'openPrivacyPolicyModal()' in html_pc
    print("[SUCCESS 1] PC 가입/로그인 레이어 이용약관 및 개인정보방침 최상위 z-index 모달 탑재 검증 완료!")

    # 2. m_base.html 모바일 메인 페이지 렌더링 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'openMobileTermsModal()' in html_m
    assert 'openMobilePrivacyModal()' in html_m
    assert 'window.openMobileTermsModal = openMobileTermsModal' in html_m
    assert 'm.style.zIndex = \'2000000\'' in html_m
    print("[SUCCESS 2] 모바일 가입/로그인 모달 약관 및 개인정보방침 팝업 레이어 바인딩 검증 완료!")

    # 3. login_notice.html 로그인 안내 팝업 레이어 렌더링 검증
    res_notice = client.get('/upload')
    html_notice = res_notice.get_data(as_text=True)
    assert '이용약관' in html_notice
    assert '개인정보 처리방침' in html_notice
    print("[SUCCESS 3] 출전등록 미로그인 팝업 레이어 이용약관 및 개인정보방침 링크 탑재 검증 완료!")

    print("\n[FINAL SUCCESS] 가입/로그인 시 이용약관 및 개인정보방침 팝업 레이어 완벽 구현 검증 완료!")

if __name__ == '__main__':
    test_terms_privacy_popup_layer()
