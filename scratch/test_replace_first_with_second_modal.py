import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_replace_first_with_second_modal():
    client = app.test_client()

    # 1. login_notice.html 템플릿 렌더링 검증
    with app.test_request_context():
        from flask import render_template
        rendered = render_template('login_notice.html', next_url='/upload', is_mobile=False)
        assert 'Google 계정 인증' in rendered
        assert 'Google 공식 계정 선택 창으로 이동' in rendered
        assert 'PawStar 약관 및 개인정보 안내' in rendered
        assert 'SweetAlert' not in rendered
        assert 'swal2' not in rendered
        print("[SUCCESS 1] 첫 번째 SweetAlert 팝업 완전 제거 및 두 번째 Google 인증 카드로 교체 검증 완료!")

    # 2. PC /upload 및 모바일 /m/upload 렌더링 검증
    res_pc = client.get('/upload', follow_redirects=True)
    html_pc = res_pc.get_data(as_text=True)
    assert 'Google 계정 인증' in html_pc
    print("[SUCCESS 2] PC 비로그인 출전페이지 접근 시 두 번째 이미지 모달 노출 성공!")

    res_m = client.get('/m/upload', follow_redirects=True)
    html_m = res_m.get_data(as_text=True)
    assert 'Google 계정 인증' in html_m
    print("[SUCCESS 3] 모바일 비로그인 출전페이지 접근 시 두 번째 이미지 모달 노출 성공!")

    print("\n[FINAL SUCCESS] 첫번째 이미지 팝업 완전 삭제 및 두번째 이미지(Google 계정 인증 전용 모달) 통일 적용 완수!")

if __name__ == '__main__':
    test_replace_first_with_second_modal()
