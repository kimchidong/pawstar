import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_m_header_power_off_button():
    client = app.test_client()

    with client:
        # 1. 비로그인 상태일 때 모바일 상단 헤더에 회색 전원버튼(mBtnHeaderPowerOff)이 존재하고 로그아웃 전원버튼은 없음을 검증
        res_guest = client.get('/m/')
        html_guest = res_guest.get_data(as_text=True)
        assert 'id="mBtnHeaderLogout"' not in html_guest, "비로그인 상태에서는 로그아웃 활성 전원버튼이 없어야 합니다."
        assert 'id="mBtnHeaderPowerOff"' in html_guest, "비로그인 상태에서는 모바일 상단 헤더에 회색 전원버튼(mBtnHeaderPowerOff)이 표시되어야 합니다."
        assert 'fa-power-off' in html_guest, "비로그인 상태에서도 전원버튼 아이콘(fa-power-off)이 탑재되어야 합니다."
        print("[PASS 1] 비로그인 상태 회색 전원버튼(mBtnHeaderPowerOff) 정상 노출 검증 완료!")

        # 2. 로그인 상태일 때 모바일 상단 헤더에 🔴전원버튼 (fa-power-off)이 존재하는지 검증
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        res_user = client.get('/m/')
        html_user = res_user.get_data(as_text=True)
        assert 'id="mBtnHeaderLogout"' in html_user, "로그인 상태에서는 모바일 상단 헤더에 전원버튼(mBtnHeaderLogout)이 표시되어야 합니다."
        assert 'fa-power-off' in html_user, "전원버튼 아이콘(fa-power-off)이 탑재되어야 합니다."
        assert 'handleMobileDirectLogout' in html_user, "로그아웃 핸들러 함수가 바인딩되어야 합니다."
        print("[PASS 2] 로그인 상태 모바일 상단 헤더 전원버튼(fa-power-off) 정상 노출 검증 완료!")

        # 3. 모바일 프로필 카드 내 로그아웃 전원버튼(fa-power-off)도 검증
        res_profile = client.get('/m/profile')
        html_profile = res_profile.get_data(as_text=True)
        assert 'id="mBtnLogoutUser"' in html_profile
        assert 'fa-power-off' in html_profile
        print("[PASS 3] 모바일 프로필 카드 내 로그아웃 전원버튼(fa-power-off) 정상 노출 검증 완료!")

if __name__ == '__main__':
    test_m_header_power_off_button()
    print("\nALL MOBILE POWER-OFF BUTTON TESTS PASSED SUCCESSFULLY!")
