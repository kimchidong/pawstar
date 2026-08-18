import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_profile_logout_explicit():
    client = app.test_client()

    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        # 1. 모바일 메인 헤더 검증 (상단 헤더 로그아웃 버튼 제거 확인)
        res_m_header = client.get('/m/')
        html_m_header = res_m_header.get_data(as_text=True)
        assert '<a href="/m/logout" class="m-nav-header-item"' not in html_m_header, "모바일 상단 헤더에 로그아웃 버튼이 없어야 합니다."
        print("[SUCCESS 1] 상단 헤더 로그아웃 버튼 제거 확인 완료!")

        # 2. 모바일 프로필 페이지 검증 (프로필 카드 내 로그아웃 버튼 mBtnLogoutUser 정상 존재 확인)
        res_m_profile = client.get('/m/profile')
        html_m_profile = res_m_profile.get_data(as_text=True)
        assert 'id="mBtnLogoutUser"' in html_m_profile, "모바일 프로필 카드 내 mBtnLogoutUser 버튼이 정상적으로 존재해야 합니다."
        print("[SUCCESS 2] 모바일 프로필 카드 내 mBtnLogoutUser 명시적 클릭 버튼 구성 확인 완료!")

        # 3. PC 프로필 페이지 검증 (프로필 카드 내 로그아웃 버튼 btnLogoutUser 정상 존재 확인)
        res_pc_profile = client.get('/profile')
        html_pc_profile = res_pc_profile.get_data(as_text=True)
        assert 'id="btnLogoutUser"' in html_pc_profile, "PC 프로필 카드 내 btnLogoutUser 버튼이 정상적으로 존재해야 합니다."
        print("[SUCCESS 3] PC 프로필 카드 내 btnLogoutUser 명시적 클릭 버튼 구성 확인 완료!")

        # 4. 로그아웃 API 동작 수행 (/m/logout?t=12345)
        res_logout = client.get('/m/logout?t=12345', follow_redirects=False)
        assert res_logout.status_code == 302
        assert res_logout.headers.get('Location') == '/m'
        print("[SUCCESS 4] 명시적 replace URL 로그아웃 성공!")

    print("\n[FINAL SUCCESS] 모든 요청 사항 수정 및 검증 완수!")

if __name__ == '__main__':
    test_profile_logout_explicit()
