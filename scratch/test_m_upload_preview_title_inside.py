def test_m_upload_preview_title_inside():
    print("=== Testing m_upload.html Preview Title Inside Content Box ===")
    
    with open('templates/m_upload.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. Check mPreviewModalTitle is inside mPreviewModalContentBox
    box_start_idx = html_content.find('id="mPreviewModalContentBox"')
    assert box_start_idx != -1, "mPreviewModalContentBox should exist!"
    
    title_idx = html_content.find('id="mPreviewModalTitle"', box_start_idx)
    assert title_idx != -1, "mPreviewModalTitle should be inside mPreviewModalContentBox!"
    
    desc_idx = html_content.find('id="mPreviewModalDesc"', title_idx)
    assert desc_idx != -1, "mPreviewModalDesc should be below mPreviewModalTitle inside mPreviewModalContentBox!"

    print("[SUCCESS] m_upload.html preview title inside content box verified 100%!")

if __name__ == '__main__':
    test_m_upload_preview_title_inside()
