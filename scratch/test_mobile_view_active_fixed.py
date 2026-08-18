import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_mobile_view_active_fixed():
    # 1. templates/m_base.html 내 인라인 하드코딩 style 방해 요소 파기 검증
    m_base_path = os.path.join(app.root_path, 'templates', 'm_base.html')
    with open(m_base_path, 'r', encoding='utf-8') as f:
        m_base_html = f.read()

    assert 'id="mDetailBtnView"' in m_base_html
    assert 'background: #e0f2fe;' not in m_base_html
    assert 'class="m-btn-action btn-view active"' in m_base_html
    print("[SUCCESS 1] m_base.html 내 mDetailBtnView 의 인라인 방해 스타일 제거 및 active 지정 완료!")

    # 2. static/js/m_main.js 내 mBtnViewPopup active & fa-solid fa-eye 지정 검증
    m_main_js_path = os.path.join(app.root_path, 'static', 'js', 'm_main.js')
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "mBtnViewPopup.classList.add('active');" in m_main_js
    assert "icon.className = 'fa-solid fa-eye';" in m_main_js
    print("[SUCCESS 2] m_main.js 내 모바일 모달 열람 시 mDetailBtnView active 지정 검증 완료!")

    print("Mobile View Active Fixed Test Passed Successfully!")

if __name__ == '__main__':
    test_mobile_view_active_fixed()
