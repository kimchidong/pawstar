import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_login_check_before_navigate():
    client = app.test_client()

    # 1. 비로그인 PC 메인피드 접근 시 isUserLoggedIn = false & handlePcUploadNavClick 바인딩 검증
    res_pc_anon = client.get('/')
    html_pc_anon = res_pc_anon.get_data(as_text=True)
    assert 'window.isUserLoggedIn = false' in html_pc_anon
    assert 'handlePcUploadNavClick' in html_pc_anon
    assert 'onclick="return handlePcUploadNavClick(event);"' in html_pc_anon

    # 2. 실제 DB 존재하는 유저 ID로 로그인 PC 메인피드 접근 시 isUserLoggedIn = true 검증
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        res_pc_user = client.get('/')
        html_pc_user = res_pc_user.get_data(as_text=True)
        assert 'window.isUserLoggedIn = true' in html_pc_user

    # 3. 비로그인 모바일 메인피드 접근 시 handleMobileUploadNavClick 바인딩 검증
    res_m_anon = client.get('/m/')
    html_m_anon = res_m_anon.get_data(as_text=True)
    assert 'window.isUserLoggedIn' in html_m_anon
    assert 'handleMobileUploadNavClick' in html_m_anon
    assert 'onclick="return handleMobileUploadNavClick(event);"' in html_m_anon

    # 4. 실제 DB 존재하는 유저 ID로 로그인 모바일 메인피드 접근 시 isUserLoggedIn = true 검증
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'ac6b727c839d6efc379526bddf1a1fcb28bee97dfccd1222374482f0ae6b2fb8'
            sess['is_logged_in'] = True

        res_m_user = client.get('/m/')
        html_m_user = res_m_user.get_data(as_text=True)
        assert 'window.isUserLoggedIn = true' in html_m_user

    print("[FINAL SUCCESS] Login Check Before Navigation Test Passed Successfully!")

if __name__ == '__main__':
    test_login_check_before_navigate()
