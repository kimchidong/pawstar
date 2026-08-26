import os

def test_preview_card_date_format():
    upload_html_path = r"d:\dev\workspace1\pawstar\templates\upload.html"
    m_upload_html_path = r"d:\dev\workspace1\pawstar\templates\m_upload.html"

    with open(upload_html_path, 'r', encoding='utf-8') as f:
        upload_html = f.read()

    assert 'id="previewCardDate"' in upload_html
    assert 'id="previewCardDate">\n                                        방금 전' in upload_html or 'id="previewCardDate">\r\n                                        방금 전' in upload_html or '방금 전' in upload_html
    assert 'if (previewCardDate) previewCardDate.textContent = (typeof formatTimeAgo === \'function\' ? formatTimeAgo(new Date()) : \'방금 전\');' in upload_html
    print("[PASS 1] PC previewCardDate relative time format verified")

    with open(m_upload_html_path, 'r', encoding='utf-8') as f:
        m_upload_html = f.read()

    assert 'id="mPreviewCardDate"' in m_upload_html
    assert 'if (mPreviewCardDate) mPreviewCardDate.textContent = (typeof formatTimeAgo === \'function\' ? formatTimeAgo(new Date()) : \'방금 전\');' in m_upload_html
    print("[PASS 2] Mobile mPreviewCardDate relative time format verified")

if __name__ == "__main__":
    test_preview_card_date_format()
    print("ALL PREVIEW CARD DATE FORMAT TESTS PASSED SUCCESSFULLY!")
