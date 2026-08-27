import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_footer_round_card_direct_link():
    client = app.test_client()

    # 1. PC 메인 렌더링 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'location.href=\'/hall-of-fame?contest_id=' in html_pc, "PC 회차 카드 블록에 회차별 명예의 전당 이동 location.href가 설정되어야 합니다."
    assert 'event.stopPropagation()' in html_pc, "사진 썸네일 영역은 부모 카드의 회차 이동 이벤트 전파를 차단해야 합니다."
    print("[PASS 1] PC 회차 카드 블록 클릭 시 해당 회차 명예의 전당 이동 링크 검증 성공!")

    # 2. 모바일 메인 렌더링 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'location.href=\'/m/hall-of-fame?contest_id=' in html_m, "모바일 회차 카드 블록에 회차별 명예의 전당 이동 location.href가 설정되어야 합니다."
    assert 'event.stopPropagation()' in html_m
    print("[PASS 2] 모바일 회차 카드 블록 클릭 시 해당 회차 명예의 전당 이동 링크 검증 성공!")

    # 3. 회차 지정 명예의 전당 이동 검증 (제1회 지정)
    res_hof1 = client.get('/hall-of-fame?contest_id=1&desktop=true')
    assert res_hof1.status_code == 200
    html_hof1 = res_hof1.get_data(as_text=True)
    assert 'contest_id=1' in html_hof1 or '제1회' in html_hof1
    print("[PASS 3] 회차 쿼리(?contest_id=1) 지정 시 명예의 전당 특정 회차 세부 선택 렌더링 성공!")

if __name__ == '__main__':
    test_footer_round_card_direct_link()
    print("\nALL FOOTER ROUND CARD DIRECT LINK TESTS PASSED SUCCESSFULLY!")
