import os

def test_preview_modal_date_format():
    upload_html_path = r"d:\dev\workspace1\pawstar\templates\upload.html"
    m_upload_html_path = r"d:\dev\workspace1\pawstar\templates\m_upload.html"

    with open(upload_html_path, 'r', encoding='utf-8') as f:
        upload_html = f.read()

    assert "id=\"previewModalDate\"" in upload_html
    assert '⏰ {{ now_str }}' not in upload_html, "upload.html previewModalDate should not show absolute datetime string!"
    assert "'⏰ ' + currentFormattedDate" not in upload_html, "upload.html updatePreview JS should not prepend date string!"
    print("[PASS 1] upload.html previewModalDate relative time format verified")

    with open(m_upload_html_path, 'r', encoding='utf-8') as f:
        m_upload_html = f.read()

    assert "id=\"mPreviewModalDate\"" in m_upload_html
    assert "'⏰ ' + currentFormattedDate" not in m_upload_html, "m_upload.html updateMobilePreview JS should not prepend date string!"
    assert '방금 전' in m_upload_html, "m_upload.html previewModalDate should show '방금 전'!"
    print("[PASS 2] m_upload.html mPreviewModalDate relative time format verified")

if __name__ == "__main__":
    test_preview_modal_date_format()
    print("PREVIEW DATE FORMAT TESTS PASSED!")
