import os

def test_original_image_zoom():
    base_html_path = r"d:\dev\workspace1\pawstar\templates\base.html"
    m_base_html_path = r"d:\dev\workspace1\pawstar\templates\m_base.html"
    main_js_path = r"d:\dev\workspace1\pawstar\static\js\main.js"
    m_main_js_path = r"d:\dev\workspace1\pawstar\static\js\m_main.js"

    # 1. base.html 검증
    with open(base_html_path, 'r', encoding='utf-8') as f:
        base_html = f.read()
    assert 'id="originalImageModal"' in base_html
    assert 'id="ogImageZoomContainer"' in base_html
    assert 'id="ogZoomPercent"' in base_html
    assert 'zoomOriginalImage' in base_html
    print("[PASS 1] base.html 줌 컨트롤 툴바 & 뷰포트 markup 검증 성공!")

    # 2. m_base.html 검증
    with open(m_base_html_path, 'r', encoding='utf-8') as f:
        m_base_html = f.read()
    assert 'id="originalImageModal"' in m_base_html
    assert 'id="ogImageZoomContainer"' in m_base_html
    assert 'id="ogZoomPercent"' in m_base_html
    assert 'zoomOriginalImage' in m_base_html
    print("[PASS 2] m_base.html 줌 컨트롤 툴바 & 뷰포트 markup 검증 성공!")

    # 3. main.js 검증
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()
    assert 'function zoomOriginalImage(' in main_js
    assert 'function resetOriginalImageZoom(' in main_js
    assert 'container.addEventListener(\'wheel\'' in main_js
    assert 'container.addEventListener(\'dblclick\'' in main_js
    assert 'container.addEventListener(\'touchstart\'' in main_js
    print("[PASS 3] main.js 휠/드래그/핀치줌/더블클릭 엔진 검증 성공!")

    # 4. m_main.js 검증
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()
    assert 'function zoomOriginalImage(' in m_main_js
    assert 'function resetOriginalImageZoom(' in m_main_js
    assert 'container.addEventListener(\'wheel\'' in m_main_js
    assert 'container.addEventListener(\'dblclick\'' in m_main_js
    assert 'container.addEventListener(\'touchstart\'' in m_main_js
    print("[PASS 4] m_main.js 휠/드래그/핀치줌/더블클릭 엔진 검증 성공!")

if __name__ == '__main__':
    test_original_image_zoom()
    print("\nALL ORIGINAL IMAGE ZOOM & PAN TESTS PASSED SUCCESSFULLY!")
