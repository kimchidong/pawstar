import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_click_card_opens_google_auth_modal():
    # 1. static/js/main.js 파일 내 openDetailModal() 의 비로그인 분기 스크립트 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    open_detail_snippet = main_js[main_js.find('openDetailModal'):main_js.find('openDetailModal')+400]
    assert "window.location.href = '/auth/google';" not in open_detail_snippet
    assert "openGoogleAuthModal()" in open_detail_snippet
    print("[SUCCESS 1] PC 회차 카드 클릭 시 구글 계정 인증 모달 팝업 레이어 오픈 연동 검증 완수!")

    # 2. static/js/m_main.js 파일 내 openMobileDetailModal() 의 비로그인 분기 스크립트 검증
    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    open_m_detail_snippet = m_main_js[m_main_js.find('openMobileDetailModal'):m_main_js.find('openMobileDetailModal')+400]
    assert "openGoogleAuthModal()" in open_m_detail_snippet
    assert "window.location.href = '/auth/google';" not in open_m_detail_snippet
    print("[SUCCESS 2] 모바일 회차 카드 클릭 시 구글 계정 인증 모달 팝업 레이어 오픈 연동 검증 완수!")

    print("Click Card Open Google Auth Modal Test Passed Successfully!")

if __name__ == '__main__':
    test_click_card_opens_google_auth_modal()
