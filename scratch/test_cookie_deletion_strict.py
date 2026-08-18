import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_cookie_deletion_strict():
    client = app.test_client()

    # 1. 로그인 상태 가정 (세션 및 쿠키 설정)
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user_123'
            sess['is_logged_in'] = True

        client.set_cookie('user_uuid', 'U-7ecb330d-625c-4440-b47b-6e5897c541f6')
        client.set_cookie('pst_user_id', 'test_user_123')

        # 2. /m/logout 요청 시 Set-Cookie로 삭제 헤더가 발급되는지 검증
        res_m = client.get('/m/logout', follow_redirects=False)
        cookies_headers_m = res_m.headers.getlist('Set-Cookie')
        print(f"[Mobile Logout Set-Cookie Headers Count]: {len(cookies_headers_m)}")
        print("[Mobile Logout Set-Cookie]:", cookies_headers_m)

        # session 및 user_uuid 의 Max-Age=0 혹은 Expires=1970 파기 확인
        has_session_del = any('session=;' in h and ('Expires=Thu, 01 Jan 1970' in h or 'Max-Age=0' in h) for h in cookies_headers_m)
        has_uuid_del = any('user_uuid=;' in h and ('Expires=Thu, 01 Jan 1970' in h or 'Max-Age=0' in h) for h in cookies_headers_m)
        assert has_session_del is True, "session 쿠키 삭제 헤더가 발급되어야 합니다!"
        assert has_uuid_del is True, "user_uuid 쿠키 삭제 헤더가 발급되어야 합니다!"

        # 3. /logout 요청 시 Set-Cookie 검증
        res_pc = client.get('/logout', follow_redirects=False)
        cookies_headers_pc = res_pc.headers.getlist('Set-Cookie')
        has_session_del_pc = any('session=;' in h and ('Expires=Thu, 01 Jan 1970' in h or 'Max-Age=0' in h) for h in cookies_headers_pc)
        has_uuid_del_pc = any('user_uuid=;' in h and ('Expires=Thu, 01 Jan 1970' in h or 'Max-Age=0' in h) for h in cookies_headers_pc)
        assert has_session_del_pc is True
        assert has_uuid_del_pc is True

    print("\n[SUCCESS] 백엔드 및 응답 헤더 레벨에서 session, user_uuid 등 모든 쿠키 파기 검증 완료!")

if __name__ == '__main__':
    test_cookie_deletion_strict()
