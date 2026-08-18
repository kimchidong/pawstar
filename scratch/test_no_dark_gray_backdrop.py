import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_no_dark_gray_backdrop():
    client = app.test_client()

    # 1. login_notice.html 템플릿 직행 검증 (단독 어두운 회색 <body> 스타일 사멸 확인)
    with app.test_request_context():
        from flask import render_template
        rendered = render_template('login_notice.html', next_url='/m/upload', is_mobile=True)
        assert 'background: rgba(15, 23, 42, 0.75)' not in rendered
        assert 'mock-feed-bg' in rendered
        assert 'rgba(15, 23, 42, 0.45)' in rendered
        assert 'open_login=true' in rendered
        print("[SUCCESS 1] 단독 어두운 회색 팝업 배경 완전 제거 및 메인피드 가상 뷰어 연동 확인!")

    # 2. PC /upload 비로그인 접근 시 리다이렉트 이동 검증
    res_pc = client.get('/upload', follow_redirects=False)
    assert res_pc.status_code == 302
    assert 'open_login=true' in res_pc.headers.get('Location')
    print("[SUCCESS 2] PC 비로그인 출전접근 시 메인피드 배경 유지를 위한 open_login=true 리다이렉트 확인!")

    # 3. 모바일 /m/upload 비로그인 접근 시 리다이렉트 이동 검증
    res_m = client.get('/m/upload', follow_redirects=False)
    assert res_m.status_code == 302
    assert 'open_login=true' in res_m.headers.get('Location')
    print("[SUCCESS 3] 모바일 비로그인 출전접근 시 메인피드 배경 유지를 위한 open_login=true 리다이렉트 확인!")

    print("\n[FINAL SUCCESS] 상단/하단 어두운 회색 칠 팝업 배경 사멸 및 뒤 메인 피드 반투명 비침 적용 완성!")

if __name__ == '__main__':
    test_no_dark_gray_backdrop()
