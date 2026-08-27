import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_footer_recent_stars_link():
    client = app.test_client()

    # 1. PC 푸터 검증
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'href="/hall-of-fame"' in html_pc, "PC 푸터 최근 콘테스트 펫 스타 영역에 /hall-of-fame 링크가 존재해야 합니다."
    assert '최근 콘테스트 펫 스타' in html_pc
    assert 'TOP 1, 2, 3위 출전작' in html_pc
    print("[PASS 1] PC 푸터 '최근 콘테스트 펫 스타' 및 'TOP 1, 2, 3위 출전작' 클릭 링크 검증 성공!")

    # 2. 모바일 푸터 검증
    res_m = client.get('/m/')
    html_m = res_m.get_data(as_text=True)
    assert 'href="/m/hall-of-fame"' in html_m, "모바일 푸터 최근 콘테스트 펫 스타 영역에 /m/hall-of-fame 링크가 존재해야 합니다."
    assert '최근 콘테스트 펫 스타' in html_m
    assert 'TOP 1, 2, 3위 출전작' in html_m
    print("[PASS 2] 모바일 푸터 '최근 콘테스트 펫 스타' 및 'TOP 1, 2, 3위 출전작' 클릭 링크 검증 성공!")

    # 3. 명예의 전당 기본 진입 시 최신 회차 선택 검증 (PC)
    res_hof_pc = client.get('/hall-of-fame?desktop=true')
    assert res_hof_pc.status_code == 200
    html_hof_pc = res_hof_pc.get_data(as_text=True)
    assert '명예의 전당' in html_hof_pc
    print("[PASS 3] PC 명예의 전당 진입 시 최신 회차 기본 렌더링 검증 성공!")

    # 4. 명예의 전당 기본 진입 시 최신 회차 선택 검증 (Mobile)
    res_hof_m = client.get('/m/hall-of-fame')
    assert res_hof_m.status_code == 200
    html_hof_m = res_hof_m.get_data(as_text=True)
    assert '명예의 전당' in html_hof_m
    print("[PASS 4] 모바일 명예의 전당 진입 시 최신 회차 기본 렌더링 검증 성공!")

if __name__ == '__main__':
    test_footer_recent_stars_link()
    print("\nALL FOOTER RECENT STARS LINK TESTS PASSED SUCCESSFULLY!")
