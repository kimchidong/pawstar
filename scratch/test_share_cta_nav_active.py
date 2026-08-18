import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_share_cta_nav_active():
    client = app.test_client()

    # DB 상의 정식 share_sn 구하기
    valid_sn = service.get_or_create_share_sn(1, 1)

    # 1. PC share_detail.html 내 contest_id 파라미터 링크 검증
    res_share_pc = client.get(f'/share?contest_round=1&round_no=1&share_sn={valid_sn}')
    html_share_pc = res_share_pc.get_data(as_text=True)
    assert 'contest_id=1' in html_share_pc
    assert 'open_post=1_1' in html_share_pc
    print("[SUCCESS 1] PC 공유페이지 내 메인 피드 보러가기 링크에 contest_id=1 및 open_post=1_1 포함 검증 완료!")

    # 2. 모바일 m_share_detail.html 내 contest_id 파라미터 링크 검증
    res_share_m = client.get(f'/share?contest_round=1&round_no=1&share_sn={valid_sn}', headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'})
    html_share_m = res_share_m.get_data(as_text=True)
    assert 'contest_id=1' in html_share_m
    assert 'open_post=1_1' in html_share_m
    print("[SUCCESS 2] 모바일 공유페이지 내 메인 피드 보러가기 링크에 contest_id=1 및 open_post=1_1 포함 검증 완료!")

    # 3. /?contest_id=1&open_post=1_1 랜딩 시 1회차 진행 중 회차 200 OK 검증
    res_index = client.get('/?contest_id=1&open_post=1_1')
    assert res_index.status_code == 200
    print("[SUCCESS 3] 메인 피드 1회차 진행중 콘테스트 진입 (200 OK) 성공!")

    print("Share CTA Nav Active Test Passed Successfully!")

if __name__ == '__main__':
    test_share_cta_nav_active()
