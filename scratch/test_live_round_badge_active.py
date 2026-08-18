import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_live_round_badge_active():
    # 1. 16회차(진행 중 회차) 게시물 상세 데이터 가져오기
    post_detail = service.get_post_detail(16, 1)
    if not post_detail:
        post_detail = service.get_post_detail(16, '1')

    assert post_detail is not None, "16회차 게시물이 있어야 합니다."
    assert post_detail.get('is_closed') is False, "16회차는 LIVE 진행 중 회차이어야 합니다."
    print("[SUCCESS 1] DB상 제16회 차가 LIVE 진행 중(is_closed = False)으로 정확히 판별됨을 확인!")

    # 2. main.js 및 m_main.js 내 rawRound 파싱 로직 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert "let rawRound = post.CONTEST_ROUND || post.contest_round || post.contest_id;" in main_js
    print("[SUCCESS 2] main.js 내 게시물 순번(ROUND_NO) 오인 버그 파기 및 CONTEST_ROUND 추출 적용 확인!")

    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "let rawRound = postData.CONTEST_ROUND || postData.contest_round || postData.contest_id;" in m_main_js
    print("[SUCCESS 3] m_main.js 내 게시물 순번(ROUND_NO) 오인 버그 파기 및 CONTEST_ROUND 추출 적용 확인!")

    print("Live Round Badge Active Test Passed Successfully!")

if __name__ == '__main__':
    test_live_round_badge_active()
