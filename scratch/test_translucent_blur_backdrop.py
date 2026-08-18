import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_translucent_blur_backdrop():
    client = app.test_client()

    # 1. /upload 접근 시 open_login=true 302 리다이렉트
    res_pc_up = client.get('/upload', follow_redirects=False)
    assert res_pc_up.status_code == 302
    assert 'open_login=true' in res_pc_up.headers.get('Location')
    print("[SUCCESS 1] PC 비로그인 접근 시 메인피드 배경 렌더링을 위해 open_login=true 이동 확인!")

    # 2. PC 메인페이지 렌더링 내 반투명 블러 백드롭 CSS 속성 확인
    res_pc_main = client.get('/?open_login=true')
    html_pc = res_pc_main.get_data(as_text=True)
    assert 'background: rgba(15, 23, 42, 0.45)' in html_pc or 'rgba(15, 23, 42, 0.45)' in html_pc
    assert 'backdrop-filter: blur(8px)' in html_pc
    print("[SUCCESS 2] PC 메인 피드 위 Google 계정 인증 모달의 반투명 블러 비침 백드롭 속성 검증 완료!")

    # 3. 모바일 /m/upload 접근 시 open_login=true 302 리다이렉트
    res_m_up = client.get('/m/upload', follow_redirects=False)
    assert res_m_up.status_code == 302
    assert 'open_login=true' in res_m_up.headers.get('Location')
    print("[SUCCESS 3] 모바일 비로그인 접근 시 모바일 메인피드 배경 렌더링을 위해 open_login=true 이동 확인!")

    # 4. 모바일 메인페이지 렌더링 내 반투명 블러 백드롭 CSS 속성 확인
    res_m_main = client.get('/m/?open_login=true')
    html_m = res_m_main.get_data(as_text=True)
    assert 'rgba(15, 23, 42, 0.45)' in html_m
    assert 'backdrop-filter: blur(8px)' in html_m
    print("[SUCCESS 4] 모바일 메인 피드 위 Google 계정 인증 모달의 반투명 블러 비침 백드롭 속성 검증 완료!")

    print("\n[FINAL SUCCESS] 요청하신 뒤 피드 페이지 반투명 비침 블러 고급 모달 팝업 레이어 구현 완료!")

if __name__ == '__main__':
    test_translucent_blur_backdrop()
