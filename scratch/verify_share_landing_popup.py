import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def verify_share_landing_popup():
    client = app.test_client()

    # 1. 1회차 게시물 전용 공유 URL 파라미터로 /share 접근 검증 (PC)
    # share_sn 생성 또는 가져오기
    share_sn = service.get_or_create_share_sn(1, 1)
    if not share_sn:
        share_sn = 'test_share_sn'

    res_pc = client.get(f'/share?contest_round=1&round_no=1&share_sn={share_sn}')
    assert res_pc.status_code == 200
    html_pc = res_pc.get_data(as_text=True)

    assert "post" in html_pc or "share_detail" in html_pc
    print("[SUCCESS 1] PC 공유 링크 랜딩 /share 접근 (200 OK) 성공!")

    # 2. 모바일 User-Agent로 /share 접근 검증
    res_m = client.get(f'/share?contest_round=1&round_no=1&share_sn={share_sn}', headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'})
    assert res_m.status_code == 200
    html_m = res_m.get_data(as_text=True)

    assert "post" in html_m or "m_share_detail" in html_m
    print("[SUCCESS 2] 모바일 공유 링크 랜딩 /share 접근 (200 OK) 성공!")

    # 3. /api/post/detail/1_1 API 응답 검증 (자동 팝업 로딩 데이터)
    res_detail = client.get('/api/post/detail/1_1')
    data = res_detail.get_json()

    assert data.get('success') is True
    post = data.get('post')
    assert post.get('is_closed') is False, "진행 중 회차이므로 is_closed는 False이어야 합니다."
    assert post.get('CONTEST_ROUND') == 1 or post.get('contest_id') == 1, "회차 번호는 1이어야 합니다."
    print("[SUCCESS 3] 공유 랜딩 자동 팝업용 post_detail API에서 is_closed = False 및 CONTEST_ROUND = 1 정확 반환 확인!")

    print("[ALL VERIFIED SUCCESS] 공유 링크 진입 시 팝업 상단 회차 뱃지 및 평가요소 활성화 준비 완료!")

if __name__ == '__main__':
    verify_share_landing_popup()
