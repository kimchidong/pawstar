import os

def test_popup_view_inactive_for_own_posts():
    main_js_path = r"d:\dev\workspace1\pawstar\static\js\main.js"
    m_main_js_path = r"d:\dev\workspace1\pawstar\static\js\m_main.js"
    base_html_path = r"d:\dev\workspace1\pawstar\templates\base.html"
    m_base_html_path = r"d:\dev\workspace1\pawstar\templates\m_base.html"

    with open(base_html_path, 'r', encoding='utf-8') as f:
        base_html = f.read()
    assert 'id="detailBtnView"' in base_html
    assert 'class="action-btn btn-view active" id="detailBtnView"' not in base_html, "base.html should not have static 'active' class on detailBtnView!"
    print("[PASS 1] base.html static active class removed from detailBtnView")

    with open(m_base_html_path, 'r', encoding='utf-8') as f:
        m_base_html = f.read()
    assert 'id="mDetailBtnView"' in m_base_html
    assert 'class="m-btn-action btn-view active" id="mDetailBtnView"' not in m_base_html, "m_base.html should not have static 'active' class on mDetailBtnView!"
    print("[PASS 2] m_base.html static active class removed from mDetailBtnView")

    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()
    assert "detailBtnViewPopup.classList.add('active');" not in main_js, "main.js should not unconditionally add active to detailBtnViewPopup!"
    assert "btnViewPopup.classList.add('active');" not in main_js, "main.js should not unconditionally add active to btnViewPopup!"
    assert "detailBtnViewPopup.classList.toggle('active', isViewAct);" in main_js
    print("[PASS 3] main.js detailBtnView active conditional toggle verified")

    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()
    assert "mBtnViewPopup.classList.add('active');" not in m_main_js, "m_main.js should not unconditionally add active to mBtnViewPopup!"
    assert "mBtnViewPopup.classList.toggle('active', mIsViewAct);" in m_main_js or "mBtnViewPopup.classList.toggle('active', mIsInitViewAct);" in m_main_js
    print("[PASS 4] m_main.js mDetailBtnView active conditional toggle verified")

if __name__ == "__main__":
    test_popup_view_inactive_for_own_posts()
    print("ALL TESTS PASSED SUCCESSFULLY!")
