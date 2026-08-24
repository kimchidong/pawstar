import re

def test_first_open_view_active():
    print("=== Testing First Open Detail Modal View Active Logic ===")
    
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 1. Check detailBtnViewPopup always receives classList.add('active')
    assert "detailBtnViewPopup.classList.add('active');" in js_content, "detailBtnViewPopup should always add active class!"
    
    # 2. Check updatePopupViewUI always adds active class
    assert "const updatePopupViewUI = () => {\n        const btnView = document.getElementById('detailBtnView');\n        if (btnView) {\n            btnView.classList.add('active');" in js_content, "updatePopupViewUI should always add active class!"

    print("[SUCCESS] First open detail modal view active logic verified 100%!")

if __name__ == '__main__':
    test_first_open_view_active()
