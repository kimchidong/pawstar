import os

def test_popup_view_inactive_for_own_posts_and_active_for_others():
    main_js_path = r"d:\dev\workspace1\pawstar\static\js\main.js"
    m_main_js_path = r"d:\dev\workspace1\pawstar\static\js\m_main.js"

    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert "const isViewAct = isUserLoggedIn && !isMine && (!isClosedRound || !!" in main_js, "main.js isViewAct must activate immediately on first open for other users in active rounds!"
    print("[PASS 1] main.js isViewAct includes !isClosedRound for immediate popup activation")

    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert "const isViewAct = isUserLoggedIn && !isMinePost && (!isClosedRound || isViewed);" in m_main_js, "m_main.js isViewAct must activate immediately on first open for other users in active rounds!"
    print("[PASS 2] m_main.js isViewAct includes !isClosedRound for immediate popup activation")

if __name__ == "__main__":
    test_popup_view_inactive_for_own_posts_and_active_for_others()
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
