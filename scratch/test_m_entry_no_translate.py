def test_m_entry_no_translate():
    print("=== Testing Mobile Entry Number Text 1px Upward Translation ===")

    # 1. m_style.css check
    with open('static/css/m_style.css', 'r', encoding='utf-8') as f:
        css = f.read()
    assert 'transform: translateY(-1px);' in css, "m_style.css should have translateY(-1px)!"

    # 2. m_index.html check
    with open('templates/m_index.html', 'r', encoding='utf-8') as f:
        m_idx = f.read()
    assert 'transform: translateY(-1px);' in m_idx, "m_index.html span should have translateY(-1px)!"

    # 3. m_base.html check
    with open('templates/m_base.html', 'r', encoding='utf-8') as f:
        m_base = f.read()
    assert 'transform: translateY(-1px);' in m_base, "m_base.html mDetailEntryNoText should have translateY(-1px)!"

    print("[SUCCESS] Mobile entry number text 1px upward translation verified 100%!")

if __name__ == '__main__':
    test_m_entry_no_translate()
