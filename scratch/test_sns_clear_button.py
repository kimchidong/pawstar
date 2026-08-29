import os

def test_sns_clear_button():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_html_path = os.path.join(base_dir, 'templates', 'upload.html')
    m_upload_html_path = os.path.join(base_dir, 'templates', 'm_upload.html')

    with open(upload_html_path, 'r', encoding='utf-8') as f:
        upload_html = f.read()
    with open(m_upload_html_path, 'r', encoding='utf-8') as f:
        m_upload_html = f.read()

    # 1. Check PC upload.html SNS clear buttons
    for sns_id in ['uploadSnsInst', 'uploadSnsYtb', 'uploadSnsFsb', 'uploadSnsBlg']:
        assert f'id="clear_{sns_id}"' in upload_html, f"clear_{sns_id} missing in upload.html"
    assert 'function clearSnsInput(' in upload_html, "clearSnsInput function missing in upload.html"
    assert 'function updateSnsClearBtnVisibility(' in upload_html, "updateSnsClearBtnVisibility function missing in upload.html"
    assert 'window.clearSnsInput = clearSnsInput' in upload_html, "window.clearSnsInput missing in upload.html"
    assert 'window.clearMobileSnsInput = clearSnsInput' in upload_html, "window.clearMobileSnsInput missing in upload.html"
    print("[PASS 1] PC upload.html SNS clear buttons & JS functions verified!")

    # 2. Check Mobile m_upload.html SNS clear buttons
    for sns_id in ['mUploadSnsInst', 'mUploadSnsYtb', 'mUploadSnsFsb', 'mUploadSnsBlg']:
        assert f'id="clear_{sns_id}"' in m_upload_html, f"clear_{sns_id} missing in m_upload.html"
    assert 'function clearMobileSnsInput(' in m_upload_html, "clearMobileSnsInput function missing in m_upload.html"
    assert 'window.clearMobileSnsInput = clearMobileSnsInput' in m_upload_html, "window.clearMobileSnsInput missing in m_upload.html"
    assert 'window.clearSnsInput = clearMobileSnsInput' in m_upload_html, "window.clearSnsInput missing in m_upload.html"
    assert 'function updateMobileSnsClearBtnVisibility(' in m_upload_html, "updateMobileSnsClearBtnVisibility function missing in m_upload.html"
    print("[PASS 2] Mobile m_upload.html SNS clear buttons & JS functions verified!")

    print("ALL SNS CLEAR BUTTON TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_sns_clear_button()
