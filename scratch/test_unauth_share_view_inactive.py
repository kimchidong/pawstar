import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_unauth_share_view_inactive():
    client = app.test_client()

    valid_sn = service.get_or_create_share_sn(1, 1)

    # 1. 비로그인 유저 모바일 공유 페이지 접근
    res_unauth_m = client.get(f'/share?contest_round=1&round_no=1&share_sn={valid_sn}', headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'})
    html_unauth_m = res_unauth_m.get_data(as_text=True)

    # 비로그인 유저이므로 btn-view 에 active 클래스와 하드코딩 파란색이 없어야 함
    assert 'class="m-btn-action action-btn btn-view "' in html_unauth_m or 'btn-view active' not in html_unauth_m
    assert 'fa-regular fa-eye' in html_unauth_m
    print("[SUCCESS 1] 비로그인 유저 모바일 공유 페이지 접근 시 조회수 버튼 비활성화(fa-regular fa-eye) 정상 확인!")

    # 2. 비로그인 유저 PC 공유 페이지 접근
    res_unauth_pc = client.get(f'/share?contest_round=1&round_no=1&share_sn={valid_sn}')
    html_unauth_pc = res_unauth_pc.get_data(as_text=True)

    assert 'btn-view active' not in html_unauth_pc
    assert 'fa-regular fa-eye' in html_unauth_pc
    print("[SUCCESS 2] 비로그인 유저 PC 공유 페이지 접근 시 조회수 버튼 비활성화(fa-regular fa-eye) 정상 확인!")

    print("Unauth Share View Inactive Test Passed Successfully!")

if __name__ == '__main__':
    test_unauth_share_view_inactive()
