import os

def test_ytb_embed():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Check HTML containers
    base_html_path = os.path.join(base_dir, 'templates', 'base.html')
    m_base_html_path = os.path.join(base_dir, 'templates', 'm_base.html')
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        base_html = f.read()
    with open(m_base_html_path, 'r', encoding='utf-8') as f:
        m_base_html = f.read()
        
    assert 'id="detailYtbContainer"' in base_html, "detailYtbContainer missing in base.html"
    assert 'id="mDetailYtbContainer"' in m_base_html, "mDetailYtbContainer missing in m_base.html"
    print("[PASS 1] HTML YTB containers present in PC & Mobile base templates")

    # 2. Check JS logic
    main_js_path = os.path.join(base_dir, 'static', 'js', 'main.js')
    m_main_js_path = os.path.join(base_dir, 'static', 'js', 'm_main.js')
    
    with open(main_js_path, 'r', encoding='utf-8') as f:
        main_js = f.read()
    with open(m_main_js_path, 'r', encoding='utf-8') as f:
        m_main_js = f.read()

    assert 'getYouTubeVideoId' in main_js, "getYouTubeVideoId missing in main.js"
    assert 'getYouTubeVideoId' in m_main_js, "getYouTubeVideoId missing in m_main.js"
    
    assert 'detailYtbContainer' in main_js, "detailYtbContainer missing in main.js"
    assert 'mDetailYtbContainer' in m_main_js, "mDetailYtbContainer missing in m_main.js"

    # Autoplay, Mute, Playsinline, ending handler check
    for param in ['autoplay=1', 'playsinline=1', 'setupYouTubePlayerWithEnding']:
        assert param in main_js, f"{param} missing in main.js"
        assert param in m_main_js, f"{param} missing in m_main.js"
    assert 'mute=0' in main_js, "mute=0 missing in main.js"
    assert 'mute=0' in m_main_js, "mute=0 missing in m_main.js"

    print("[PASS 2] JS YouTube video embed & autoplay logic present in main.js & m_main.js")
    print("ALL YOUTUBE EMBED TESTS PASSED!")

if __name__ == '__main__':
    test_ytb_embed()
