def test_m_badge_equal_height():
    print("=== Testing Mobile Entry Badge Height & Font Size Equalization ===")

    # 1. m_style.css check
    with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
        css = f.read()
    assert 'font-size: 0.56rem !important;' in css, "m-entry-no-badge font-size should be 0.56rem!"
    assert 'padding: 0.15rem 0.42rem !important;' in css, "m-entry-no-badge padding should be 0.15rem 0.42rem!"

    # 2. m_index.html check
    with open('templates/m_index.html', 'r', encoding='utf-8') as f:
        m_idx = f.read()
    assert 'font-size: 0.56rem;' in m_idx, "m_index.html badge font-size should be 0.56rem!"
    assert 'padding: 0.15rem 0.42rem;' in m_idx, "m_index.html badge padding should be 0.15rem 0.42rem!"

    # 3. m_base.html check
    with open('templates/m_base.html', 'r', encoding='utf-8') as f:
        m_base = f.read()
    assert 'font-size: 0.56rem;' in m_base, "m_base.html badge font-size should be 0.56rem!"
    assert 'padding: 0.15rem 0.42rem;' in m_base, "m_base.html badge padding should be 0.15rem 0.42rem!"

    print("[SUCCESS] Mobile entry badge height & font size equalization verified 100%!")

if __name__ == '__main__':
    test_m_badge_equal_height()
