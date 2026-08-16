import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.contest_service import service

def test_google_nickname():
    res = service.google_login_or_register(
        google_id="test_new_google_id_99999",
        email="testuser99999@gmail.com",
        name="홍길동",
        picture=""
    )
    print("Generated user_info:", res)
    assert res['nickname'] != "홍길동"
    assert res['nickname'] != "testuser99999"
    print("TEST PASSED: Nickname is random generated:", res['nickname'])

if __name__ == "__main__":
    test_google_nickname()
