import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = app.test_client()

test_urls = [
    ("https://www.instagram.com/this_user_definitely_does_not_exist_99999999", False),
    ("https://www.youtube.com/watch?v=invalid_id_9999", False),
    ("https://www.facebook.com/invalid_user_99999999", False),
    ("https://blog.naver.com/invalid_blog_id_99999999", False),
    ("https://www.instagram.com/", False),
    ("https://www.youtube.com/", False),
    ("https://blog.naver.com/", False),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True), # Rickroll (Valid)
    ("https://blog.naver.com/naver_blog", True) # Naver blog official (Valid)
]

print("=== CHECK URL STATUS TEST ===")
for url, expected in test_urls:
    res = client.post('/api/check_url_status', json={'url': url})
    data = res.get_json()
    is_ok = data.get('ok', False)
    status = data.get('status')
    print(f"URL: {url:<65} => ok: {str(is_ok):<5} (Expected: {str(expected):<5}), status: {status}")
