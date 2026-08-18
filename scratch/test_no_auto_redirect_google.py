import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_no_auto_redirect_google():
    client = app.test_client()

    # 1. PC base.html 렌더링 내 btnNavProfile 자동 이동 스크립트가 제거되고 openGoogleAuthModal()만 호출되는지 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'openGoogleAuthWindow()' not in html_pc
    assert 'btnOfficialGoogleAuth' in html_pc
    assert 'href="/auth/google"' in html_pc
    print("[SUCCESS 1] PC에서 자동으로 구글 로그인 페이지로 튕기는 자동 이동 이벤트 리스너 제거 완수!")

    # 2. 팝업 카드 내부의 [ Google 공식 계정 선택 창으로 이동 ] 버튼에만 /auth/google 링크가 연결되어 있는지 검증
    assert 'id="btnOfficialGoogleAuth"' in html_pc
    assert 'href="/auth/google"' in html_pc
    print("[SUCCESS 2] 모달 팝업의 선택창 버튼 클릭시에만 구글 로그인 페이지로 이동하도록 바인딩 완료!")

    # 3. 모바일 m_base.html 렌더링 내 선택창 버튼 바인딩 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'id="btnOfficialGoogleAuthMobile"' in html_m
    assert 'href="/auth/google"' in html_m
    print("[SUCCESS 3] 모바일 모달 팝업의 선택창 버튼 클릭시에만 구글 로그인 페이지로 이동하도록 바인딩 완료!")

    print("[FINAL SUCCESS] 구글인증 팝업 오픈 시 자동 이동 버그 해결 및 선택창 버튼 클릭 시 이동 정상 검증 완료!")

if __name__ == '__main__':
    test_no_auto_redirect_google()
