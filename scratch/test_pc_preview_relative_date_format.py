import os
import sys

def test_pc_preview_relative_date_format():
    main_js_path = r"d:\dev\workspace1\pawstar\static\js\main.js"
    m_main_js_path = r"d:\dev\workspace1\pawstar\static\js\m_main.js"
    upload_html_path = r"d:\dev\workspace1\pawstar\templates\upload.html"

    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()

    assert 'function formatTimeAgo(' in main_js
    assert 'match(/^(\\d{4})[-/](\\d{1,2})[-/](\\d{1,2})[ T](\\d{1,2}):(\\d{1,2})(?::(\\d{1,2}))?/' in main_js
    assert "return '방금 전';" in main_js

    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert 'function formatTimeAgo(' in m_main_js
    assert 'match(/^(\\d{4})[-/](\\d{1,2})[-/](\\d{1,2})[ T](\\d{1,2}):(\\d{1,2})(?::(\\d{1,2}))?/' in m_main_js

    with open(upload_html_path, 'r', encoding='utf-8') as f:
        upload_html = f.read()

    assert 'if (previewCardDate) previewCardDate.textContent = (typeof formatTimeAgo === \'function\' ? formatTimeAgo(new Date()) : \'방금 전\');' in upload_html
    assert 'if (previewModalDate) previewModalDate.textContent = (typeof formatTimeAgo === \'function\' ? formatTimeAgo(new Date()) : \'방금 전\');' in upload_html

    print("[SUCCESS] PC preview relative date format logic verified!")

if __name__ == "__main__":
    test_pc_preview_relative_date_format()
