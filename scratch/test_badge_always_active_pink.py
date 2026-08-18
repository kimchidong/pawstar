import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_badge_always_active_pink():
    # 1. main.js 회차 뱃지 핑크보라빛 활성화 통일 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert "color: #db2777; background: #fce7f3" in main_js
    assert "background: #f1f5f9; border: 1.5px solid #cbd5e1" not in main_js
    print("[SUCCESS 1] PC 상세 팝업 회차 뱃지 핑크보라빛 활성화 스타일 100% 통일 검증 완료!")

    # 2. m_main.js 회차 뱃지 핑크보라빛 활성화 통일 검증
    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "color: #db2777; background: #fce7f3" in m_main_js
    assert "background: #f1f5f9; border: 1.5px solid #cbd5e1" not in m_main_js
    print("[SUCCESS 2] 모바일 상세 팝업 회차 뱃지 핑크보라빛 활성화 스타일 100% 통일 검증 완료!")

    print("Badge Always Active Pink Test Passed Successfully!")

if __name__ == '__main__':
    test_badge_always_active_pink()
