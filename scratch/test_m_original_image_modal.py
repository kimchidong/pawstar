def test_m_original_image_modal():
    print("=== Testing Mobile Original Image Lightbox Modal Implementation ===")

    # 1. m_base.html check
    with open('templates/m_base.html', 'r', encoding='utf-8') as f:
        m_base_html = f.read()
    assert 'id="originalImageModal"' in m_base_html, "originalImageModal should exist in m_base.html!"
    assert 'id="originalImageViewImg"' in m_base_html, "originalImageViewImg should exist in m_base.html!"
    assert 'openOriginalImageModal(this.src)' in m_base_html, "mDetailImg should have openOriginalImageModal onclick!"

    # 2. m_main.js check
    with open('static/js/m_main.js', 'r', encoding='utf-8') as f:
        m_main_js = f.read()
    assert 'function openOriginalImageModal(' in m_main_js, "openOriginalImageModal should be defined in m_main.js!"
    assert 'function closeOriginalImageModal(' in m_main_js, "closeOriginalImageModal should be defined in m_main.js!"

    print("[SUCCESS] Mobile Original Image Lightbox Modal implementation verified 100%!")

if __name__ == '__main__':
    test_m_original_image_modal()
