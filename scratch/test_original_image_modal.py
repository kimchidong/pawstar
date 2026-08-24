def test_original_image_modal():
    print("=== Testing Original Image Lightbox Modal Implementation ===")

    # 1. base.html check
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_html = f.read()
    assert 'id="originalImageModal"' in base_html, "originalImageModal should exist in base.html!"
    assert 'id="originalImageViewImg"' in base_html, "originalImageViewImg should exist in base.html!"
    assert 'openOriginalImageModal(this.src)' in base_html, "detailImg should have openOriginalImageModal onclick!"

    # 2. m_base.html check
    with open('templates/m_base.html', 'r', encoding='utf-8') as f:
        m_base_html = f.read()
    assert 'openOriginalImageModal(this.src)' in m_base_html, "mDetailImg should have openOriginalImageModal onclick!"

    # 3. main.js check
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        main_js = f.read()
    assert 'function openOriginalImageModal(' in main_js, "openOriginalImageModal should be defined in main.js!"
    assert 'function closeOriginalImageModal(' in main_js, "closeOriginalImageModal should be defined in main.js!"

    print("[SUCCESS] Original Image Lightbox Modal implementation verified 100%!")

if __name__ == '__main__':
    test_original_image_modal()
