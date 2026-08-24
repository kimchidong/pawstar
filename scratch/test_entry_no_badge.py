def test_entry_no_badge():
    print("=== Testing Entry Number Badge Placement (Bottom Left of Post Image) ===")

    # 1. index.html check
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        idx_html = f.read()
    assert 'class="entry-no-badge"' in idx_html, "entry-no-badge should be in index.html!"
    assert 'left: 0.65rem; bottom: 0.65rem;' in idx_html, "entry-no-badge should be positioned bottom left!"

    # 2. m_index.html check
    with open('templates/m_index.html', 'r', encoding='utf-8') as f:
        m_idx_html = f.read()
    assert 'class="m-entry-no-badge"' in m_idx_html, "m-entry-no-badge should be in m_index.html!"
    assert 'left: 0.45rem; bottom: 0.45rem;' in m_idx_html, "m-entry-no-badge should be positioned bottom left!"

    # 3. base.html detail modal check
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_html = f.read()
    assert 'id="detailEntryNoBadge"' in base_html, "detailEntryNoBadge should be in base.html!"
    assert 'left: 0.85rem; bottom: 0.85rem;' in base_html, "detailEntryNoBadge should be positioned bottom left!"

    # 4. m_base.html detail modal check
    with open('templates/m_base.html', 'r', encoding='utf-8') as f:
        m_base_html = f.read()
    assert 'id="mDetailEntryNoBadge"' in m_base_html, "mDetailEntryNoBadge should be in m_base.html!"
    assert 'left: 0.65rem; bottom: 0.65rem;' in m_base_html, "mDetailEntryNoBadge should be positioned bottom left!"

    print("[SUCCESS] Entry number badge bottom-left placement verified 100%!")

if __name__ == '__main__':
    test_entry_no_badge()
