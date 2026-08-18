import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.contest_service import service

def test_live_vs_closed_round_popup():
    client = app.test_client()

    # 1. 1회차(진행 중 회차) 데이터 조회 및 is_closed = False 검증
    post_detail = service.get_post_detail(1, 1)
    if not post_detail:
        post_detail = service.get_post_detail(1, '1')

    assert post_detail is not None
    assert post_detail.get('is_closed') is False, "1회차는 진행 중 회차이어야 합니다."
    print("[SUCCESS 1] 진행 중인 1회차 게시물의 is_closed = False 확인 완료!")

    # 2. main.js & m_main.js 내 handles logic 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert "if (commentFormContainer) commentFormContainer.style.display = 'flex';" in main_js
    assert "el.style.pointerEvents = '';" in main_js
    print("[SUCCESS 2] PC main.js 내 진행 중 회차 시 평가 요소 및 댓글창 활성화 코드 검증 완료!")

    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "if (mCommentFormContainer) mCommentFormContainer.style.display = 'flex';" in m_main_js
    assert "el.style.pointerEvents = '';" in m_main_js
    print("[SUCCESS 3] 모바일 m_main.js 내 진행 중 회차 시 평가 요소 및 댓글창 활성화 코드 검증 완료!")

    print("Live VS Closed Round Popup Test Passed Successfully!")

if __name__ == '__main__':
    test_live_vs_closed_round_popup()
