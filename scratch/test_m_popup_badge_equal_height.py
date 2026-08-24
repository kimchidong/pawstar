def test_m_popup_badge_equal_height():
    print("=== Testing Mobile Detail Modal Badge Height & Font Size Equalization ===")

    # 1. m_style.css check for #mDetailRankBadge .m-card-badge
    with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
        css = f.read()
    assert 'font-size: 0.56rem !important;' in css, "m-card-badge in modal should have font-size 0.56rem!"
    assert 'padding: 0.15rem 0.42rem !important;' in css, "m-card-badge in modal should have padding 0.15rem 0.42rem!"

    # 2. m_main.js check for mBadgeEl innerHTML inline styles
    with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
        js = f.read()
    assert 'font-size: 0.82rem;' not in js, "m_main.js should no longer have font-size: 0.82rem for m-card-badge!"
    assert 'padding: 0.15rem 0.42rem;' in js, "m_main.js should use padding 0.15rem 0.42rem for modal badges!"

    print("[SUCCESS] Mobile detail modal badge height & font size equalization verified 100%!")

if __name__ == '__main__':
    test_m_popup_badge_equal_height()
