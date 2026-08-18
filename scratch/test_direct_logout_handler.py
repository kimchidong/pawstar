import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_direct_logout_handler():
    client = app.test_client()

    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        # 1. m_profile.html 렌더링 내 handleMobileDirectLogout(event) 인라인 검증
        res_m = client.get('/m/profile')
        html_m = res_m.get_data(as_text=True)
        assert 'onclick="handleMobileDirectLogout(event)"' in html_m
        assert 'function handleMobileDirectLogout' in html_m
        print("[SUCCESS 1] m_profile.html 내 원터치 인라인 로그아웃 핸들러 바인딩 검증 완료!")

        # 2. profile.html 렌더링 내 handlePcDirectLogout(event) 인라인 검증
        res_pc = client.get('/profile')
        html_pc = res_pc.get_data(as_text=True)
        assert 'onclick="handlePcDirectLogout(event)"' in html_pc
        assert 'function handlePcDirectLogout' in html_pc
        print("[SUCCESS 2] profile.html 내 원터치 인라인 로그아웃 핸들러 바인딩 검증 완료!")

        # 3. /api/logout 호출 검증 (POST)
        res_api_logout = client.post('/api/logout')
        assert res_api_logout.status_code == 200
        print("[SUCCESS 3] /api/logout POST 백엔드 파기 정상 완료!")

        # 4. /m/logout?t=12345 호출 검증 (GET)
        res_m_logout = client.get('/m/logout?t=12345', follow_redirects=False)
        assert res_m_logout.status_code == 302
        assert res_m_logout.headers.get('Location') == '/m'
        print("[SUCCESS 4] /m/logout?t=12345 즉시 리다이렉트 성공!")

    print("\n[FINAL SUCCESS] 프로필 카드 로그아웃 버튼 원터치 파기 및 리다이렉트 완벽 처리 검증 완료!")

if __name__ == '__main__':
    test_direct_logout_handler()
