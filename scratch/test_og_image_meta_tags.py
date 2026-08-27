import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_og_image_meta_tags():
    # 1. 파일 존재 여부 검증
    og_image_path = r"d:\dev\workspace1\pawstar\static\image\app\og_image.png"
    assert os.path.exists(og_image_path), f"오픈그래프 대표 이미지 파일 {og_image_path} 가 존재해야 합니다."
    assert os.path.getsize(og_image_path) > 10000, "이미지 파일 용량이 정상이어야 합니다."
    print("[PASS 1] 오픈그래프 전용 대표 이미지 생성 및 저장 확인 완료!")

    # 2. Flask 렌더링 시 og:image 태그 검증
    client = app.test_client()
    res_pc = client.get('/')
    html_pc = res_pc.get_data(as_text=True)
    assert 'static/image/app/og_image.png' in html_pc, "base.html og:image 경로가 og_image.png 로 변경되어야 합니다."
    assert 'og:image:width' in html_pc
    assert 'og:image:height' in html_pc
    print("[PASS 2] PC base.html 오픈그래프 메타 태그 정상 렌더링 확인 완료!")

    res_mobile = client.get('/m/')
    html_mobile = res_mobile.get_data(as_text=True)
    assert 'static/image/app/og_image.png' in html_mobile, "m_base.html og:image 경로가 og_image.png 로 변경되어야 합니다."
    assert 'og:image:width' in html_mobile
    assert 'og:image:height' in html_mobile
    print("[PASS 3] 모바일 m_base.html 오픈그래프 메타 태그 정상 렌더링 확인 완료!")

if __name__ == '__main__':
    test_og_image_meta_tags()
    print("\nALL OPEN GRAPH IMAGE TESTS PASSED SUCCESSFULLY!")
