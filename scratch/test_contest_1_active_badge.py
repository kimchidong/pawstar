import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_contest_1_active_badge():
    client = app.test_client()

    # 1. 백엔드 is_contest_closed(1) 상태 확인
    is_closed = service.is_contest_closed(1)
    assert is_closed is False, "1회차는 진행 중 회차(CONTEST_STAT = G001C001)이어야 합니다."
    print("[SUCCESS 1] 1회차 콘테스트가 진행 중(is_closed = False)으로 DB 및 서비스 층에서 정확히 판별됨!")

    # 2. 1회차 게시물 상세 API 조회시 is_closed = False 확인
    post_detail = service.get_post_detail(1, 1)
    if not post_detail:
        post_detail = service.get_post_detail(1, '1')

    assert post_detail is not None, "1회차 게시물이 존재해야 합니다."
    assert post_detail.get('is_closed') is False, "1회차 게시물의 is_closed는 False이어야 합니다."
    print("[SUCCESS 2] 1회차 게시물 상세 정보의 is_closed가 False로 정상 반환됨!")

    # 3. /api/post/detail/1_1 API 응답 검증
    res_api = client.get('/api/post/detail/1_1')
    json_data = res_api.get_json()
    assert json_data.get('success') is True
    post_data = json_data.get('post')
    assert post_data.get('is_closed') is False
    print("[SUCCESS 3] /api/post/detail/1_1 API에서 is_closed = False 정상 응답 검증 완료!")

    print("[FINAL SUCCESS] 1회차 콘테스트 LIVE 진행 중 회차 뱃지 활성화 검증 완료!")

if __name__ == '__main__':
    test_contest_1_active_badge()
