import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_pc_share_nav_badge_active():
    # 1. main.js 내 updatePcContestBadgeUI 구현 및 이중 호출 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert 'const updatePcContestBadgeUI = (pObj) => {' in main_js
    assert main_js.count('updatePcContestBadgeUI(post);') >= 2
    print("[SUCCESS 1] main.js 내 updatePcContestBadgeUI 헬퍼 구현 및 비동기 수신 시 갱신 보장 확인!")

    # 2. 1회차 게시물 상세 API 및 is_closed = False 검증
    post_detail = service.get_post_detail(1, 1)
    assert post_detail is not None
    assert post_detail.get('is_closed') is False
    print("[SUCCESS 2] 1회차 진행 중 게시물 정보의 is_closed = False 검증 완료!")

    print("PC Share Nav Badge Active Test Passed Successfully!")

if __name__ == '__main__':
    test_pc_share_nav_badge_active()
