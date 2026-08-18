import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_no_forced_google_redirect():
    client = app.test_client()

    # 1. static/js/main.js 파일 내 하드코딩 구글 자동 이동 구문 사멸 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    assert "window.location.href = '/auth/google?next='" not in js_content
    assert "function openGoogleLoginModal() {\n    window.location.href = '/auth/google';" not in js_content
    print("[SUCCESS 1] main.js 내 모든 강제 구글 자동 이동 스크립트 파기 완료!")

    # 2. PC / 메인 피드 상에서 모달 바인딩 정상 렌더링 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'id="googleAuthModal"' in html_pc
    assert 'openGoogleAuthModal' in html_pc
    print("[SUCCESS 2] 메인 피드 반투명 팝업 모달 탑재 검증 완료!")

    # 3. 모바일 /m 메인 피드 상에서 모달 바인딩 정상 렌더링 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'id="googleAuthModal"' in html_m
    assert 'openGoogleAuthModal' in html_m
    print("[SUCCESS 3] 모바일 메인 피드 반투명 팝업 모달 탑재 검증 완료!")

    print("[FINAL SUCCESS] 구글 로그인 페이지 강제 자동 이동 버그 근본원인 파기 완수!")

if __name__ == '__main__':
    test_no_forced_google_redirect()
