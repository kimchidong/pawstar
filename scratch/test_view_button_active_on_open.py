import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_view_button_active_on_open():
    # 1. main.js 내 조회수 버튼 active 활성화 및 fa-solid fa-eye 검증
    main_js_path = os.path.join(app.root_path, 'static', 'js', 'main.js')
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert "detailBtnViewPopup.classList.add('active');" in main_js
    assert "icon.className = 'fa-solid fa-eye';" in main_js
    print("[SUCCESS 1] PC 상세 모달 오픈 시 조회수 버튼 active 보라빛 활성화 코드 검증 완료!")

    # 2. m_main.js 내 조회수 버튼 active 활성화 및 fa-solid fa-eye 검증
    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "mBtnViewPopup.classList.add('active');" in m_main_js
    assert "icon.className = 'fa-solid fa-eye';" in m_main_js
    print("[SUCCESS 2] 모바일 상세 모달 오픈 시 조회수 버튼 active 보라빛 활성화 코드 검증 완료!")

    print("View Button Active On Open Test Passed Successfully!")

if __name__ == '__main__':
    test_view_button_active_on_open()
