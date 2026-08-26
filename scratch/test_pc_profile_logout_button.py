import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_pc_profile_logout_button():
    client = app.test_client()

    with client:
        # 로그인 상태 세션 주입 (실제 DB 유저 ID)
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        res = client.get('/profile')
        html = res.get_data(as_text=True)

        assert 'id="btnLogoutUser"' in html, "PC 프로필 페이지 내 btnLogoutUser 로그아웃 버튼이 존재해야 합니다."
        assert 'fa-power-off' in html, "로그아웃 버튼에 전원 아이콘(fa-power-off)이 포함되어야 합니다."
        assert 'handlePcDirectLogout' in html, "handlePcDirectLogout 이벤트 핸들러가 연결되어야 합니다."
        print("[PASS] PC 프로필 페이지 회원 탈퇴 옆 로그아웃 전원버튼(btnLogoutUser) 추가 검증 완료!")

if __name__ == '__main__':
    test_pc_profile_logout_button()
    print("ALL PC PROFILE LOGOUT BUTTON TESTS PASSED!")
