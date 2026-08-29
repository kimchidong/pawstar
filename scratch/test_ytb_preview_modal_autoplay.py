import os

def test_ytb_preview_modal_autoplay():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_html_path = os.path.join(base_dir, 'templates', 'upload.html')
    m_upload_html_path = os.path.join(base_dir, 'templates', 'm_upload.html')

    with open(upload_html_path, 'r', encoding='utf-8') as f:
        upload_html = f.read()
    with open(m_upload_html_path, 'r', encoding='utf-8') as f:
        m_upload_html = f.read()

    # 1. PC upload.html check
    assert 'desktopModal = document.getElementById(\'previewModalBackdrop\')' in upload_html, "PC modal display check missing"
    assert 'isModalOpen && typeof setupYouTubePlayerWithEnding' in upload_html, "PC updatePreview modal open check missing"
    assert 'openDesktopPreviewModal' in upload_html and 'setupYouTubePlayerWithEnding(\'previewYtbContainer\'' in upload_html, "PC open modal YouTube trigger missing"
    assert 'closeDesktopPreviewModal' in upload_html and 'window.previewYtbPlayer.destroy' in upload_html, "PC close modal player cleanup missing"
    print("[PASS 1] PC upload.html YouTube modal-only playback logic verified!")

    # 2. Mobile m_upload.html check
    assert 'mModal = document.getElementById(\'mPreviewModalBackdrop\')' in m_upload_html, "Mobile modal display check missing"
    assert 'isMModalOpen && typeof setupYouTubePlayerWithEnding' in m_upload_html, "Mobile updateMobilePreview modal open check missing"
    assert 'openMobilePreviewModal' in m_upload_html and 'setupYouTubePlayerWithEnding(\'mPreviewYtbContainer\'' in m_upload_html, "Mobile open modal YouTube trigger missing"
    assert 'closeMobilePreviewModal' in m_upload_html and 'window.mPreviewYtbPlayer.destroy' in m_upload_html, "Mobile close modal player cleanup missing"
    print("[PASS 2] Mobile m_upload.html YouTube modal-only playback logic verified!")

    print("ALL YOUTUBE PREVIEW AUTOPLAY TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_ytb_preview_modal_autoplay()
