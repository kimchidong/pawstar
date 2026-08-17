"""
Paw Star - Python Flask Web Application
슬로건: "반려동물도 스타가 될 수 있다."
"""

import os
import datetime
import uuid
import shutil
import random
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response, flash
from werkzeug.utils import secure_filename
from services.contest_service import service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pawstar_secret_key_2026'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)
SESSION_TIMEOUT_SECONDS = 1800  # 30분 (1800초) 무활동 타임아웃

def finalize_temp_profile_image(avatar_icon):
    """
    /static/image/temp/profile/ 경로에 있는 임시 프로필 이미지를
    영구 저장 디렉터리 /static/image/profile/{YYYY}/{MM}/ 로 이동합니다.
    """
    if not avatar_icon or not isinstance(avatar_icon, str) or not (avatar_icon.startswith("/static/image/temp/profile/") or avatar_icon.startswith("/static/image/temp/")):
        return avatar_icon

    now = datetime.datetime.now()
    year_str = now.strftime("%Y")
    month_str = now.strftime("%m")
    
    perm_dir = os.path.join(app.root_path, 'static', 'image', 'profile', year_str, month_str)
    temp_dir = os.path.join(app.root_path, 'static', 'image', 'temp', 'profile')

    filename = os.path.basename(avatar_icon)
    clean_name = filename[5:] if filename.startswith("temp_") else filename
    perm_filename = f"profile_{clean_name}" if not clean_name.startswith("profile_") else clean_name

    src_file = os.path.join(temp_dir, filename)
    if not os.path.exists(src_file):
        old_temp = os.path.join(app.root_path, 'static', 'image', 'temp', filename)
        if os.path.exists(old_temp):
            src_file = old_temp

    if not os.path.exists(perm_dir):
        os.makedirs(perm_dir, exist_ok=True)

    dest_file = os.path.join(perm_dir, perm_filename)
    if os.path.exists(src_file):
        shutil.move(src_file, dest_file)

    thumb_filename = filename.replace(".webp", "_thumb.webp")
    perm_thumb_filename = perm_filename.replace(".webp", "_thumb.webp")
    src_thumb = os.path.join(temp_dir, thumb_filename)
    if not os.path.exists(src_thumb):
        old_thumb = os.path.join(app.root_path, 'static', 'image', 'temp', thumb_filename)
        if os.path.exists(old_thumb):
            src_thumb = old_thumb

    dest_thumb = os.path.join(perm_dir, perm_thumb_filename)
    if os.path.exists(src_thumb):
        shutil.move(src_thumb, dest_thumb)

    return f"/static/image/profile/{year_str}/{month_str}/{perm_filename}"


@app.template_filter('m_time_ago')
def m_time_ago_filter(dt_val):
    if not dt_val:
        return ''
    try:
        dt_str = str(dt_val).strip()
        dt = None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d', '%Y-%m-%d %H:%M'):
            try:
                dt = datetime.datetime.strptime(dt_str.split('.')[0], fmt)
                break
            except Exception:
                pass
        if not dt:
            return dt_str[:10]

        now = datetime.datetime.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0:
            return '방금 전'

        if seconds < 60:
            return '방금 전'
        minutes = seconds // 60
        if minutes < 60:
            return f'{minutes}분 전'
        hours = minutes // 60
        if hours < 24:
            return f'{hours}시간 전'
        days = hours // 24
        if days < 30:
            return f'{days}일 전'
        months = days // 30
        if months < 12:
            return f'{months}개월 전'
        years = months // 12
        return f'{years}년 전'
    except Exception:
        return str(dt_val)[:10]

@app.before_request
def check_session_timeout():
    """ 웹 서비스 이용(요청) 중 아무런 액션 없이 30분(1800초) 경과 시 세션 자동 만료 파기 처리 """
    now_ts = datetime.datetime.now().timestamp()
    last_act = session.get('last_activity')

    if session.get('user_id'):
        if last_act and (now_ts - last_act > SESSION_TIMEOUT_SECONDS):
            session.clear()
            session['logged_out_reason'] = 'timeout'
        else:
            session['last_activity'] = now_ts


@app.context_processor
def inject_global_vars():
    """ 템플릿 전역에서 사용할 회원 프로필 정보 전달 """
    user_id = session.get('user_id')
    is_logged_in = bool(user_id and not session.get('logged_out', False))

    if is_logged_in:
        # DB에 실제 회원 레코드가 존재하는지 검증 (DB 초기화/Truncate 시 세션 자동 리셋)
        if not service.is_user_exists(user_id):
            session.clear()
            is_logged_in = False
            current_user = {
                'nickname': '프로필',
                'NK_NM': '프로필',
                'profile_img': '/static/image/profile/default_profile.png'
            }
        else:
            profile_data = service.get_user_profile(user_id)
            current_user = profile_data.get('user_info', {})
            # 64자리 해시 닉네임 노출 방지 안전 처리
            from services.contest_service import sanitize_nickname
            clean_nk = sanitize_nickname(current_user.get('NK_NM') or current_user.get('nickname'), fallback="집사")
            current_user['NK_NM'] = clean_nk
            current_user['nickname'] = clean_nk
    else:
        current_user = {
            'nickname': '프로필',
            'NK_NM': '프로필',
            'profile_img': '/static/image/profile/default_profile.png'
        }

    footer_recent_rounds = []
    try:
        def get_rank_sort_key(item):
            cd = str(item.get('AWARD_CD') or item.get('award_cd') or '')
            rk = item.get('RANKING') or item.get('rank_no') or item.get('ranking')
            if 'P001A101' in cd or rk == 1 or rk == '1':
                return 1
            elif 'P001A102' in cd or rk == 2 or rk == '2':
                return 2
            elif 'P001A103' in cd or rk == 3 or rk == '3':
                return 3
            return 99

        contests_list = service.get_contests()
        for c in (contests_list or []):
            c_id = c.get('CONTEST_ROUND') or c.get('contest_id')
            res = service.get_hall_of_fame(contest_id=c_id)
            if res and isinstance(res, list) and len(res) > 0:
                rank1_list = []
                rank2_list = []
                rank3_list = []
                for w in res:
                    if w.get('AWARD_PART') == 'G002P001' or w.get('award_part') == 'G002P001':
                        rk = get_rank_sort_key(w)
                        if rk == 1:
                            rank1_list.append(w)
                        elif rk == 2:
                            rank2_list.append(w)
                        elif rk == 3:
                            rank3_list.append(w)
                
                rank_slots = []
                if rank1_list:
                    rank_slots.append({'rank': 1, 'stars': rank1_list})
                if rank2_list:
                    rank_slots.append({'rank': 2, 'stars': rank2_list})
                if rank3_list:
                    rank_slots.append({'rank': 3, 'stars': rank3_list})

                if rank_slots:
                    footer_recent_rounds.append({
                        'contest': c,
                        'rank_slots': rank_slots
                    })
            if len(footer_recent_rounds) >= 2:
                break
        
        # 가장 최근 회차 순서(회차 내림차순: 제11회 -> 제10회)로 정렬
        footer_recent_rounds.sort(key=lambda x: int(x['contest'].get('CONTEST_ROUND') or x['contest'].get('contest_id') or 0), reverse=True)

    except Exception as e:
        print("footer recent rounds error:", e)
        footer_recent_rounds = []

    return {
        'contests': service.get_contests(),
        'pet_kinds': service.get_pet_kinds(),
        'app_slogan': '반려동물도 스타가 될 수 있다.',
        'current_user': current_user,
        'is_logged_in': is_logged_in,
        'footer_recent_rounds': footer_recent_rounds
    }

# --- 로그인 / 로그아웃 라우트 ---

@app.route('/logout')
@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    """ 사용자 로그아웃 처리 """
    session.clear()
    session['logged_out'] = True
    if request.is_json or request.path.startswith('/api'):
        return jsonify({'success': True, 'message': '성공적으로 로그아웃되었습니다.'})
    return redirect(url_for('index'))

@app.route('/withdraw', methods=['POST', 'GET'])
@app.route('/api/auth/withdraw', methods=['POST'])
def withdraw():
    """ 회원 탈퇴 처리 API (구글 인증 회원의 경우 Google 동의 권한도 자동 철회/Revoke) """
    user_id = session.get('user_id')
    if not user_id:
        if request.is_json or request.path.startswith('/api'):
            return jsonify({'success': False, 'message': '로그인된 상태가 아닙니다.'}), 401
        return redirect(url_for('index'))

    # 구글 소셜 회원일 경우 구글 동의 권한 철회 API 호출 (Google OAuth Revoke Token)
    access_token = session.get('access_token')
    if access_token:
        try:
            requests.post(
                'https://oauth2.googleapis.com/revoke',
                params={'token': access_token},
                headers={'content-type': 'application/x-www-form-urlencoded'},
                timeout=5
            )
            print(f"[Google Revoke] 구글 연동 권한 및 동의 철회 성공: {user_id}")
        except Exception as err:
            print(f"[Google Revoke Warning] 구글 동의 철회 중 경고 발생: {err}")

    service.delete_user(user_id)
    session.clear()
    session['logged_out'] = True

    if request.is_json or request.path.startswith('/api'):
        return jsonify({'success': True, 'message': 'PawStar 회원 탈퇴 및 Google 서버의 계정 연동 동의 철회가 성공적으로 처리되었습니다. 그동안 이용해주셔서 감사합니다. 🐾'})
    return redirect(url_for('index'))

def get_post_login_redirect_url(is_mobile=False):
    """
    공유 정보(share_info)가 세션에 존재할 때,
    - 과거(종료) 회차인 경우: 메인 피드('/m/' 또는 '/')
    - 현재 진행 중인 회차인 경우: 메인 피드 + open_post 쿼리 파라미터('/m/?open_post=X_Y' 또는 '/?open_post=X_Y')
    반환하며, 없는 경우 None 리턴
    """
    share_info = session.get('share_info')
    if share_info and isinstance(share_info, dict):
        is_closed = share_info.get('is_closed', False)
        post_id = share_info.get('post_id') or (f"{share_info.get('contest_round')}_{share_info.get('round_no')}" if share_info.get('contest_round') and share_info.get('round_no') else None)
        
        if is_closed:
            return '/m/' if is_mobile else '/'
        else:
            if post_id:
                return f"/m/?open_post={post_id}" if is_mobile else f"/?open_post={post_id}"
            return '/m/' if is_mobile else '/'
    return None

@app.route('/privacy')
def privacy_page():
    """ PawStar 개인정보 처리 안내 웹 페이지 """
    return render_template('privacy.html')

@app.route('/m/privacy')
def m_privacy_page():
    """ PawStar 개인정보 처리 안내 모바일 페이지 """
    return render_template('m_privacy.html')

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    """ 로그인 API (user_id & password) """
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()

    if not user_id or not password:
        return jsonify({'success': False, 'message': '아이디와 사용자인증번호(비밀번호)를 모두 입력해주세요.'}), 400

    success, result = service.authenticate_user(user_id, password)
    if success:
        # 공유 유입 접속 후 기존 회원 로그인 시 PST_CONTEST_SHARE 기록, 공유 카운트 및 점수 +1 반영
        process_signup_share_referral(new_user_id=user_id)

        is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
        target_url = get_post_login_redirect_url(is_mobile=is_mobile)

        saved_share_info = session.get('share_info')
        session.clear()
        session['user_id'] = user_id
        session['last_activity'] = datetime.datetime.now().timestamp()
        if saved_share_info:
            session['share_info'] = saved_share_info
        session.pop('logged_out', None)
        return jsonify({'success': True, 'message': f'{result["nickname"]}님 환영합니다!', 'user': result, 'target_url': target_url})
    else:
        return jsonify({'success': False, 'message': result}), 401

def process_signup_share_referral(new_user_id=None):
    """ 공유 링크 유입 가입/로그인 시 PST_CONTEST_SHARE 저장 및 공유 카운트/점수 1 증가 처리 헬퍼 """
    share_info = session.get('share_info')
    if share_info and isinstance(share_info, dict):
        c_round = share_info.get('contest_round')
        r_no = share_info.get('round_no')
        s_sn = share_info.get('share_sn')
        if c_round and r_no and s_sn:
            try:
                service.increment_share_count_on_signup(c_round, r_no, s_sn, user_id=new_user_id)
            except Exception as e:
                print("process_signup_share_referral error:", e)

@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    """ 회원가입 및 즉시 로그인 API """
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    nickname = data.get('nickname', '').strip()
    password = data.get('password', '').strip()
    profile_img = data.get('profile_img', '').strip()

    if not user_id or not nickname or not password:
        return jsonify({'success': False, 'message': '아이디, 닉네임, 사용자인증번호(비밀번호)는 필수 입력 사항입니다.'}), 400

    if service.is_user_exists(user_id):
        return jsonify({'success': False, 'message': '이미 사용 중인 아이디입니다.'}), 400

    # 임시 이미지 디렉터리에 있으면 최종 static/image/profile/YYYY/MM 으로 이동
    if profile_img:
        profile_img = finalize_temp_profile_image(profile_img)

    new_user = service.register_user(user_id, nickname, password, profile_img)

    # 공유 유입 회원가입 시 PST_CONTEST_SHARE 기록, 공유 카운트 및 점수 +1 반영
    process_signup_share_referral(new_user_id=user_id)

    is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
    target_url = get_post_login_redirect_url(is_mobile=is_mobile)

    session.clear()
    session['user_id'] = user_id
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({'success': True, 'message': '회원가입이 완료되었습니다!', 'user': new_user, 'target_url': target_url})

@app.route('/api/auth/setup_profile', methods=['POST'])
def api_auth_setup_profile():
    """ 닉네임, 프로필 이미지 및 사용자인증번호(PIN) 직접 입력을 통한 회원가입 API """
    data = request.json or {}
    nickname = data.get('nickname', '').strip()
    password = data.get('password', '').strip()
    profile_img = data.get('profile_img', '').strip()

    if not nickname:
        return jsonify({'success': False, 'message': '집사 닉네임을 입력해주세요.'}), 400

    if not password:
        return jsonify({'success': False, 'message': '로그인 시 사용할 사용자인증번호를 직접 입력해주세요.'}), 400

    auto_uuid = f"user_{uuid.uuid4().hex[:8]}"

    if profile_img:
        profile_img = finalize_temp_profile_image(profile_img)

    new_user = service.register_user(auto_uuid, nickname, password, profile_img)

    # 공유 유입 회원가입 시 PST_CONTEST_SHARE 기록, 공유 카운트 및 점수 +1 반영
    process_signup_share_referral(new_user_id=auto_uuid)

    is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
    target_url = get_post_login_redirect_url(is_mobile=is_mobile)

    session.clear()
    session['user_id'] = auto_uuid
    session['has_setup'] = True
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({
        'success': True,
        'message': f'프로필 설정 및 회원가입이 성공적으로 완료되었습니다!',
        'auth_code': password,
        'user': new_user,
        'target_url': target_url
    })

# Load environment variables from .env file directly if python-dotenv is not active
def load_env_file():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k not in os.environ or not os.environ[k]:
                            os.environ[k] = v
        except Exception as e:
            print(f"[Env Load Warning] {e}")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

load_env_file()

import importlib.util

def _get_config_web():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.web.py'),
        os.path.join(os.getcwd(), 'config.web.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_web", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.web.py 파일을 찾을 수 없습니다.")

def get_google_config():
    load_env_file()
    config_web = _get_config_web()
    return config_web.get_google_config()

GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI = get_google_config()




@app.route('/auth/google')
def auth_google_redirect():
    """ 팝업 창을 구글 공식 OAuth 2.0 Authorization Code 인증 페이지로 직접 리다이렉트 (response_type=code) """
    is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
    target_url = get_post_login_redirect_url(is_mobile=is_mobile)

    next_url = request.args.get('next') or request.args.get('return_url') or target_url or '/'
    session['next_url'] = next_url
    client_id, client_secret, redirect_uri = get_google_config()
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=email%20profile&"
        f"prompt=select_account"
    )
    return redirect(google_auth_url)

@app.route('/auth/google/callback')
def auth_google_callback():
    """
    구글 본체 인증 완료 후 콜백 받아서 처리.
    Server-to-Server 방식으로 GOOGLE_CLIENT_SECRET을 사용하여 code -> access_token 교환 및 유저 프로필 검증
    """
    code = request.args.get('code')
    error = request.args.get('error')
    next_url = session.get('next_url')

    # 인가 코드가 없는 경우 (또는 에러/클라이언트 직접 호출)
    if not code:
        return render_template('google_callback.html', error=error or '인증 코드가 전송되지 않았습니다.', target_url=next_url)

    client_id, client_secret, redirect_uri = get_google_config()
    if not client_secret:
        return render_template('google_callback.html', error='서버 환경 변수 GOOGLE_CLIENT_SECRET이 설정되지 않았습니다. .env 파일을 확인해주세요.', target_url=next_url)

    # 1. Google OAuth Token Endpoint로 GOOGLE_CLIENT_SECRET을 사용하여 Server-to-Server 검증 요청
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret, # 서버에서 안전하게 Secret을 사용하여 구글 서버에 인증
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        token_res = requests.post(token_url, data=token_payload, timeout=10)
        token_data = token_res.json()

        access_token = token_data.get('access_token')
        if not access_token:
            print(f"[Google OAuth Error] Token Exchange Failed: {token_data}")
            return render_template('google_callback.html', error=token_data.get('error_description', '구글 토큰 검증 실패'), target_url=next_url)

        # 2. 발급받은 access_token으로 Google UserInfo API 호출 및 유저 정보 검증
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_res = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'}, timeout=10)
        user_data = userinfo_res.json()

        email = user_data.get('email')
        google_id = user_data.get('sub')
        name = user_data.get('name') or (email.split('@')[0] if email else '집사')
        picture = user_data.get('picture') or ''

        if not email or not google_id:
            return render_template('google_callback.html', error='구글 프로필 정보 수신 실패', target_url=next_url)

        # 3. PawStar 서비스 회원 가입/로그인 처리
        user_info = service.google_login_or_register(google_id, email, name, picture)

        if user_info:
            process_signup_share_referral(new_user_id=user_info['user_id'])

        saved_next_url = session.get('next_url') or '/'
        session.clear()
        session['user_id'] = user_info['user_id']
        session['user'] = user_info
        session['profile_img'] = user_info['profile_img']
        session['access_token'] = access_token
        session['is_logged_in'] = True
        session['last_activity'] = datetime.datetime.now().timestamp()
        session.pop('logged_out', None)
        session['next_url'] = saved_next_url

        msg = f"{user_info['nickname']}님, Google 계정({email}) 인증으로 로그인되었습니다!"
        resp = make_response(render_template('google_callback.html', success=True, message=msg, user=user_info, target_url=saved_next_url))
        resp.set_cookie('pst_user_id', user_info['user_id'], max_age=365*24*3600)
        return resp
    except Exception as err:
        print(f"[Google OAuth Exception] {err}")
        return render_template('google_callback.html', error=str(err), target_url=next_url)


@app.route('/api/auth/google', methods=['POST'])
def api_auth_google():
    """ 구글 인증 전용 로그인 & 회원가입 API (수동/이메일 선택 호환) """
    data = request.json or {}
    email = (data.get('email') or '').strip()

    if not email:
        return jsonify({'success': False, 'message': 'Google 계정 이메일을 선택하거나 입력해주세요.'}), 400

    google_id = data.get('google_id') or f"g_{abs(hash(email))}"
    name = data.get('name') or email.split('@')[0]
    picture = data.get('picture') or data.get('profile_img') or ''

    user_info = service.google_login_or_register(google_id, email, name, picture)

    if user_info:
        process_signup_share_referral(new_user_id=user_info['user_id'])

    is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
    target_url = get_post_login_redirect_url(is_mobile=is_mobile)

    session.clear()
    session['user_id'] = user_info['user_id']
    session['user'] = user_info
    session['profile_img'] = user_info['profile_img']
    session['is_logged_in'] = True
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({
        'success': True,
        'message': f'{user_info["nickname"]}님, Google 계정({email}) 인증으로 성공적으로 로그인되었습니다!',
        'user': user_info,
        'target_url': target_url
    })

def is_mobile_user_agent():
    """ 클라이언트 User-Agent를 판별하여 모바일 기기 접속 여부 반환 """
    ua = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone', 'opera mini']
    return any(k in ua for k in mobile_keywords)

def get_current_user_id():
    """ 
    로그인한 회원 유저 ID 반환 (로그아웃/비로그인 시 None 반환)
    """
    if session.get('user_id'):
        return session['user_id']
    return None

@app.route('/share')
@app.route('/m/share')
def route_share():
    """ 전용 공유주소(CONTEST_ROUND, ROUND_NO, SHARE_SN) 유입 전용 랜딩 라우트 """
    contest_round = request.args.get('contest_round') or request.args.get('contest_id')
    round_no = request.args.get('round_no')
    share_sn = request.args.get('share_sn')

    is_mobile = request.path.startswith('/m') or is_mobile_user_agent()
    current_user_id = get_current_user_id()
    is_logged_in = bool(current_user_id)

    is_closed = False
    post = None
    if contest_round and round_no:
        # 1. 이미 로그인된 회원이 공유 주소로 유입된 경우: 공유 카운트 및 점수 즉시 가산
        if current_user_id and share_sn:
            try:
                service.increment_share_count_on_signup(int(contest_round), int(round_no), str(share_sn), user_id=current_user_id)
            except Exception as e:
                print("route_share increment_share_count error:", e)

        # 2. 로그인 여부 불문 조회수(+1) 무조건 즉시 반영 (IP 기준 익명 조회 기록 지원)
        try:
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            service.increase_view_count(contest_round, round_no, view_user_id=current_user_id, client_ip=client_ip)
        except Exception as e:
            print("route_share increase_view_count error:", e)

        # 3. 로그인 여부 불문 공유 유입 정보를 세션에 보존 (미로그인 유저가 가입/로그인 시 공유 점수 자동 반영)
        if share_sn:
            session['share_info'] = {
                'contest_round': int(contest_round),
                'round_no': int(round_no),
                'share_sn': str(share_sn),
                'post_id': f"{contest_round}_{round_no}"
            }

        # 최신 반영된 게시물 정보 (조회수, 공유수, 점수, actions 4요소) 가져오기
        post = service.get_post_detail(contest_round, round_no, current_user_id, share_sn=share_sn)
        if post:
            is_closed = bool(
                post.get('is_closed') or 
                post.get('closed') or 
                (post.get('STATUS_CD') == 'G001C002') or 
                (post.get('CONTEST_STAT') == 'G001C002')
            )
            session['share_info']['is_closed'] = is_closed

    template_name = 'm_share_detail.html' if is_mobile else 'share_detail.html'
    return render_template(
        template_name,
        post=post,
        is_logged_in=is_logged_in,
        current_user_id=current_user_id,
        contest_round=contest_round,
        round_no=round_no,
        share_sn=share_sn,
        is_closed=is_closed
    )

@app.route('/api/post/detail/<path:post_id>', methods=['GET'])
def api_post_detail(post_id):
    """ 단건 게시물 상세 정보 조회 API (자동 팝업 오픈용) """
    contest_round = None
    round_no = None
    post_id_str = str(post_id)
    if '_' in post_id_str:
        parts = post_id_str.split('_', 1)
        contest_round = parts[0]
        round_no = parts[1]
    else:
        round_no = post_id_str
    
    current_user_id = get_current_user_id()
    post = None
    if contest_round and round_no:
        post = service.get_post_detail(contest_round, round_no, current_user_id)
    
    if post:
        return jsonify({'success': True, 'post': post})
    return jsonify({'success': False, 'message': '게시물을 찾을 수 없습니다.'}), 404

@app.route('/api/contest/share_url', methods=['GET', 'POST'])
def api_contest_share_url():
    """ 게시글 전용 공유주소(CONTEST_ROUND, ROUND_NO, SHARE_SN) 생성/조회 API """
    data = request.json if (request.is_json and request.json) else request.args
    contest_round = data.get('contest_round') or data.get('contest_id')
    round_no = data.get('round_no')

    if not contest_round or not round_no:
        return jsonify({'success': False, 'message': 'contest_round와 round_no가 필요합니다.'}), 400

    share_sn = service.get_or_create_share_sn(contest_round, round_no)
    if not share_sn:
        return jsonify({'success': False, 'message': '전용 공유주소 생성 실패'}), 500

    base_url = request.host_url.rstrip('/')
    share_url = f"{base_url}/share?contest_round={contest_round}&round_no={round_no}&share_sn={share_sn}"
    return jsonify({
        'success': True,
        'contest_round': int(contest_round),
        'round_no': int(round_no),
        'share_sn': share_sn,
        'share_url': share_url
    })

# --- PC 전용 라우트 (1280px 고정) ---

# 1. 홈 (콘테스트 게시물 메인)
@app.route('/')
def index():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_index', **request.args))

    contest_id_arg = request.args.get('contest_id', type=int)
    if not contest_id_arg:
        active_c = service.get_current_contest()
        contest_id = active_c.get('CONTEST_ROUND') if active_c else 1
    else:
        contest_id = contest_id_arg

    sort_type = request.args.get('sort', 'latest') # latest(최신등록순), popular(인기순), trending(최근급상승)
    search_q = request.args.get('q', '')
    pet_type = request.args.get('pet_type', 'all')
    page = request.args.get('page', 1, type=int)
    current_user_id = get_current_user_id()

    current_contest = service.get_contest(contest_id)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=12, user_id=current_user_id)

    response = make_response(render_template(
        'index.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res,
        sort_type=sort_type,
        search_q=search_q,
        pet_type=pet_type
    ))
    if current_user_id:
        response.set_cookie('pst_user_id', current_user_id, max_age=365*24*3600)
    else:
        response.delete_cookie('pst_user_id')
    return response

# 📜 개인정보 처리 방침 (Privacy Policy)
@app.route('/privacy')
@app.route('/m/privacy')
def privacy_policy():
    if request.path.startswith('/m') or (is_mobile_user_agent() and not request.args.get('desktop')):
        return render_template('m_privacy.html')
    return render_template('privacy.html')

# 📜 이용약관 (Terms of Service)
@app.route('/terms')
@app.route('/m/terms')
def terms_of_service():
    if request.path.startswith('/m') or (is_mobile_user_agent() and not request.args.get('desktop')):
        return render_template('m_terms.html')
    return render_template('terms.html')

# 2. 명예의 전당 (Hall of Fame)
@app.route('/hall-of-fame')
def hall_of_fame():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_hall_of_fame', **request.args))

    contests = service.get_closed_contests()
    contest_id_arg = request.args.get('contest_id', type=int)
    
    if contest_id_arg and any((c.get('CONTEST_ROUND') == contest_id_arg or c.get('contest_id') == contest_id_arg) for c in contests):
        contest_id = contest_id_arg
    elif contests:
        contest_id = contests[0].get('CONTEST_ROUND') or contests[0].get('contest_id')
    else:
        contest_id = None

    current_user_id = get_current_user_id()
    winners = service.get_hall_of_fame(contest_id=contest_id, user_id=current_user_id)
    current_contest = service.get_contest(contest_id) if (contest_id and any((c.get('CONTEST_ROUND') == contest_id or c.get('contest_id') == contest_id) for c in contests)) else (contests[0] if contests else None)

    return render_template(
        'hall_of_fame.html',
        contests=contests,
        current_contest=current_contest,
        winners=winners
    )

# 3. 최근 급상승 메뉴
@app.route('/profile')
def profile():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_profile', **request.args))

    target_user_id = request.args.get('user_id')
    current_user_id = session.get('user_id') if not session.get('logged_out') else None

    # 마이프로필 조회 (user_id 쿼리가 없거나 본인 ID 지정인 경우)
    if not target_user_id or target_user_id == current_user_id:
        if not current_user_id:
            # 로그인되어 있지 않으면 로그인 모달이 뜨는 메인 피드로 이동
            return redirect(url_for('index', open_login='true'))
        user_id = current_user_id
    else:
        user_id = target_user_id

    contest_id = request.args.get('contest_id', 'all')
    profile_data = service.get_user_profile(user_id, contest_id=contest_id)

    return render_template(
        'profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=profile_data['my_posts'],
        my_awards=profile_data['my_awards'],
        contests=service.get_contests(),
        selected_contest_id=contest_id
    )

# --- 모바일 전용 별도 라우트 (m_ 접두사 템플릿 독립 제공) ---

@app.route('/m/')
@app.route('/m')
def m_index():
    contest_id_arg = request.args.get('contest_id', type=int)
    if not contest_id_arg:
        active_c = service.get_current_contest()
        contest_id = active_c.get('CONTEST_ROUND') if active_c else 1
    else:
        contest_id = contest_id_arg

    sort_type = request.args.get('sort', 'latest')
    search_q = request.args.get('q', '')
    pet_type = request.args.get('pet_type', 'all')
    page = request.args.get('page', 1, type=int)
    current_user_id = get_current_user_id()

    current_contest = service.get_contest(contest_id)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=10, user_id=current_user_id)

    response = make_response(render_template(
        'm_index.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res,
        sort_type=sort_type,
        search_q=search_q,
        pet_type=pet_type,
        pet_kinds=service.get_pet_kinds()
    ))
    if current_user_id:
        response.set_cookie('pst_user_id', current_user_id, max_age=365*24*3600)
    else:
        response.delete_cookie('pst_user_id')
    return response

@app.route('/api/m/posts')
def api_m_posts():
    contest_id_arg = request.args.get('contest_id', type=int)
    if not contest_id_arg:
        active_c = service.get_current_contest()
        contest_id = active_c.get('CONTEST_ROUND') if active_c else 1
    else:
        contest_id = contest_id_arg

    sort_type = request.args.get('sort', 'latest')
    search_q = request.args.get('q', '')
    pet_type = request.args.get('pet_type', 'all')
    page = request.args.get('page', 1, type=int)
    current_user_id = get_current_user_id()

    current_contest = service.get_contest(contest_id)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=12, user_id=current_user_id)

    return jsonify({
        'success': True,
        'current_contest': current_contest,
        'posts': paginated_res['posts'],
        'pagination': paginated_res,
        'sort_type': sort_type,
        'search_q': search_q,
        'pet_type': pet_type
    })

@app.route('/m/hall-of-fame')
def m_hall_of_fame():
    contests = service.get_closed_contests()
    contest_id_arg = request.args.get('contest_id', type=int)
    
    if contest_id_arg and any((c.get('CONTEST_ROUND') == contest_id_arg or c.get('contest_id') == contest_id_arg) for c in contests):
        contest_id = contest_id_arg
    elif contests:
        contest_id = contests[0].get('CONTEST_ROUND') or contests[0].get('contest_id')
    else:
        contest_id = None

    current_user_id = get_current_user_id()
    winners = service.get_hall_of_fame(contest_id=contest_id, user_id=current_user_id)
    current_contest = service.get_contest(contest_id) if (contest_id and any((c.get('CONTEST_ROUND') == contest_id or c.get('contest_id') == contest_id) for c in contests)) else (contests[0] if contests else None)

    return render_template(
        'm_hall_of_fame.html',
        contests=contests,
        current_contest=current_contest,
        winners=winners
    )

@app.route('/m/profile')
def m_profile():
    target_user_id = request.args.get('user_id')
    current_user_id = session.get('user_id') if not session.get('logged_out') else None

    # 마이프로필 조회 (user_id 쿼리가 없거나 본인 ID 지정인 경우)
    if not target_user_id or target_user_id == current_user_id:
        if not current_user_id:
            # 로그인되어 있지 않으면 모바일 메인 피드로 이동하며 로그인 유도
            return redirect(url_for('m_index', open_login='true'))
        user_id = current_user_id
    else:
        user_id = target_user_id

    contest_id = request.args.get('contest_id', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    profile_data = service.get_user_profile(user_id, contest_id=contest_id)
    all_my_posts = profile_data['my_posts']
    total_count = len(all_my_posts)
    total_pages = max(1, (total_count + per_page - 1) // per_page)

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paged_my_posts = all_my_posts[start_idx:end_idx]

    my_posts_pagination = {
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

    return render_template(
        'm_profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=paged_my_posts,
        my_posts_pagination=my_posts_pagination,
        my_awards=profile_data['my_awards'],
        contests=service.get_contests(),
        selected_contest_id=contest_id
    )

@app.route('/m/admin')
def m_admin():
    return render_template('m_admin.html', contests=service.get_contests(), winners=service.winners)

# -------------------------------------------------------------
# 출전 신청(펫 자랑하기) 파일 저장 도우미 & 전용 페이지 라우트
# -------------------------------------------------------------
def save_uploaded_media(file):
    if not file or file.filename == '':
        return None

    upload_dir = os.path.join(app.root_path, 'static', 'image', 'post')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    now = datetime.datetime.now()
    filename = secure_filename(file.filename)
    unique_name = f"post_{int(now.timestamp())}_{uuid.uuid4().hex[:8]}.webp"
    file_path = os.path.join(upload_dir, unique_name)

    try:
        from PIL import Image
        image = Image.open(file.stream)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail((1280, 1280), getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        image.save(file_path, "WEBP", quality=90)
    except Exception as err:
        print(f"[Media Upload Warning] Fallback to raw save: {err}")
        file.seek(0)
        fallback_name = f"post_{int(now.timestamp())}_{filename if filename else 'photo.jpg'}"
        file.save(os.path.join(upload_dir, fallback_name))
        return f"/static/image/post/{fallback_name}"

    return f"/static/image/post/{unique_name}"

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    user_id = session.get('user_id') or request.form.get('user_id') or 'user1'

    contests = service.get_contests()
    current_contest = service.get_current_contest() or (contests[0] if contests else None)
    
    if request.method == 'POST':
        raw_cid = request.form.get('contest_id')
        if raw_cid and str(raw_cid).isdigit():
            contest_id = int(raw_cid)
        else:
            contest_id = (current_contest.get('CONTEST_ROUND') or current_contest.get('contest_id') or 13) if current_contest else 13

        user_id = session.get('user_id') or request.form.get('user_id') or 'user1'
        pet_name = (request.form.get('pet_name') or '').strip()
        pet_type = (request.form.get('pet_type') or '').strip()
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        sns_inst = (request.form.get('sns_inst') or '').strip()
        sns_ytb = (request.form.get('sns_ytb') or '').strip()
        sns_fsb = (request.form.get('sns_fsb') or '').strip()
        sns_blg = (request.form.get('sns_blg') or '').strip()
        
        # 1. 동물 종류
        if not pet_type:
            flash('🐾 반려동물 종류를 선택해 주세요.', 'danger')
            return redirect('/upload')
        # 2. 이름
        if not pet_name:
            flash('🐶 반려동물 이름을 입력해 주세요.', 'danger')
            return redirect('/upload')
        # 3. 자랑 제목
        if not title:
            flash('✨ 자랑 제목을 입력해 주세요.', 'danger')
            return redirect('/upload')
        if len(title) > 80:
            flash('✨ 자랑 제목은 80자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')
        # 4. 인스타그램 주소
        if sns_inst and len(sns_inst) > 200:
            flash('🔗 인스타그램 주소는 200자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')
        # 5. 유튜브 주소
        if sns_ytb and len(sns_ytb) > 200:
            flash('🔗 유튜브 주소는 200자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')
        # 6. 페이스북 주소
        if sns_fsb and len(sns_fsb) > 200:
            flash('🔗 페이스북 주소는 200자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')
        # 7. 블로그 주소
        if sns_blg and len(sns_blg) > 200:
            flash('🔗 블로그 주소는 200자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')

        file = request.files.get('media_file')
        # 8. 출전 사진 파일 첨부
        if not file or file.filename == '':
            flash('🖼️ 출전 사진 파일 첨부가 필요합니다. 사진을 선택해 주세요.', 'danger')
            return redirect('/upload')
        # 9. 자랑 내용 및 소개글
        if not content:
            flash('📝 자랑 내용 및 소개글을 입력해 주세요.', 'danger')
            return redirect('/upload')
        if len(content) > 100:
            flash('📝 자랑 내용 및 소개글은 100자 이내로 입력해 주세요.', 'danger')
            return redirect('/upload')

        next_post_id = service.get_next_post_id()
        full_path1, full_path2 = process_paw_images_dual(file, contest_id, next_post_id)

        res = service.create_post(
            contest_id, user_id, pet_name, pet_type, title, content, 
            file_path1=full_path1, file_path2=full_path2, force_post_id=next_post_id,
            sns_inst=sns_inst, sns_ytb=sns_ytb, sns_fsb=sns_fsb, sns_blg=sns_blg
        )

        if isinstance(res, dict) and not res.get('success'):
            flash(f"⚠️ {res.get('message', '출전 등록에 실패했습니다.')}", 'danger')
            return redirect('/upload')

        flash('🎉 출전 등록이 성공적으로 완료되었습니다! 🐾', 'success')
        return redirect(f'/?contest_id={contest_id}&uploaded=true')

    contest_id = (current_contest.get('CONTEST_ROUND') or current_contest.get('contest_id') or 1) if current_contest else 1
    my_entry_count = service.get_user_contest_entry_count(contest_id, user_id)
    remaining_entry_count = max(0, 5 - my_entry_count)
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template(
        'upload.html', 
        current_contest=current_contest, 
        contests=contests,
        my_entry_count=my_entry_count,
        remaining_entry_count=remaining_entry_count,
        pet_kinds=service.get_pet_kinds(),
        now_str=now_str
    )

@app.route('/m/upload', methods=['GET', 'POST'])
def m_upload_page():
    user_id = session.get('user_id') or request.form.get('user_id') or 'user1'

    contests = service.get_contests()
    current_contest = service.get_current_contest() or (contests[0] if contests else None)

    if request.method == 'POST':
        raw_cid = request.form.get('contest_id')
        if raw_cid and str(raw_cid).isdigit():
            contest_id = int(raw_cid)
        else:
            contest_id = (current_contest.get('CONTEST_ROUND') or current_contest.get('contest_id') or 13) if current_contest else 13

        user_id = session.get('user_id') or request.form.get('user_id') or 'user1'
        pet_name = (request.form.get('pet_name') or '').strip()
        pet_type = (request.form.get('pet_type') or '').strip()
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        sns_inst = (request.form.get('sns_inst') or '').strip()
        sns_ytb = (request.form.get('sns_ytb') or '').strip()
        sns_fsb = (request.form.get('sns_fsb') or '').strip()
        sns_blg = (request.form.get('sns_blg') or '').strip()

        if not pet_name:
            flash('🐶 반려동물 이름을 입력해주세요.', 'danger')
            return redirect('/m/upload')
        if not pet_type:
            flash('🐾 반려동물 종류를 선택해주세요.', 'danger')
            return redirect('/m/upload')
        if not title:
            flash('✨ 자랑 제목을 입력해주세요.', 'danger')
            return redirect('/m/upload')
        if not content:
            flash('📝 자랑 내용 및 소개글을 입력해주세요.', 'danger')
            return redirect('/m/upload')

        file = request.files.get('media_file')
        if not file or file.filename == '':
            flash('🖼️ 출전 사진 파일 첨부가 필요합니다. 사진을 선택해주세요.', 'danger')
            return redirect('/m/upload')

        next_post_id = service.get_next_post_id()
        full_path1, full_path2 = process_paw_images_dual(file, contest_id, next_post_id)

        res = service.create_post(
            contest_id, user_id, pet_name, pet_type, title, content, 
            file_path1=full_path1, file_path2=full_path2, force_post_id=next_post_id,
            sns_inst=sns_inst, sns_ytb=sns_ytb, sns_fsb=sns_fsb, sns_blg=sns_blg
        )

        if isinstance(res, dict) and not res.get('success'):
            flash(f"⚠️ {res.get('message', '출전 등록에 실패했습니다.')}", 'danger')
            return redirect('/m/upload')

        flash('🎉 출전 등록이 성공적으로 완료되었습니다! 🐾', 'success')
        return redirect(f'/m/?contest_id={contest_id}&uploaded=true')

    contest_id = current_contest.get('CONTEST_ROUND', 1) if current_contest else 1
    my_entry_count = service.get_user_contest_entry_count(contest_id, user_id)
    remaining_entry_count = max(0, 5 - my_entry_count)
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template(
        'm_upload.html', 
        current_contest=current_contest, 
        contests=contests,
        my_entry_count=my_entry_count,
        remaining_entry_count=remaining_entry_count,
        pet_kinds=service.get_pet_kinds(),
        now_str=now_str
    )



# 4-1. 프로필 이미지 임시 업로드 API (plamodelshop 호환)
@app.route('/upload/profile', methods=['POST'])
def upload_profile():
    if 'profile_img' not in request.files:
        return jsonify({"success": False, "message": "업로드할 파일이 존재하지 않습니다."}), 400
    file = request.files['profile_img']
    if file.filename == '':
        return jsonify({"success": False, "message": "선택된 파일이 없습니다."}), 400
    
    if file:
        now = datetime.datetime.now()
        temp_dir = os.path.join(app.root_path, 'static', 'image', 'temp', 'profile')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
            
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        unique_name = f"temp_profile_{int(now.timestamp())}_{uuid.uuid4().hex[:8]}.webp"
        
        file_path = os.path.join(temp_dir, unique_name)
        try:
            from PIL import Image
            image = Image.open(file.stream)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGBA")
            
            # 1. 원본 이미지 리사이징 (Max 600x600)
            main_image = image.copy()
            main_image.thumbnail((600, 600), getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
            main_image.save(file_path, "WEBP", quality=90)

            # 2. 썸네일 리사이징 (Max 120x120)
            thumb_path = file_path.replace(".webp", "_thumb.webp")
            thumb_image = image.copy()
            thumb_image.thumbnail((120, 120), getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
            thumb_image.save(thumb_path, "WEBP", quality=85)
        except Exception as err:
            print(f"[PIL Warning] PIL image processing fallback: {err}")
            file.seek(0)
            file.save(file_path)
            thumb_path = file_path.replace(".webp", "_thumb.webp")
            file.seek(0)
            file.save(thumb_path)

        
        web_url = f"/static/image/temp/profile/{unique_name}"
        return jsonify({"success": True, "url": web_url})

# 4-2. 프로필 수정 API (닉네임 중복 검사 적용)
@app.route('/api/profile/update', methods=['POST'])
def api_profile_update():
    data = request.json or {}
    user_id = (data.get('user_id') or session.get('user_id') or request.cookies.get('pst_user_id') or 'user1').strip()
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'require_login': True}), 401
    nickname = data.get('nickname')
    profile_img = data.get('profile_img')
    sns_inst = (data.get('sns_inst') or '').strip()
    sns_ytb = (data.get('sns_ytb') or '').strip()
    sns_fsb = (data.get('sns_fsb') or '').strip()
    sns_blg = (data.get('sns_blg') or '').strip()
    
    success, message, updated_user = service.update_user_profile(
        user_id=user_id,
        nickname=nickname,
        profile_img=profile_img,
        sns_inst=sns_inst,
        sns_ytb=sns_ytb,
        sns_fsb=sns_fsb,
        sns_blg=sns_blg
    )
    if not success:
        return jsonify({'success': False, 'message': message}), 400

    # 세션 내 프로필 정보 갱신
    if updated_user:
        if isinstance(session.get('user'), dict):
            session['user'].update(updated_user)
        else:
            session['user'] = updated_user
        session['nickname'] = updated_user.get('NK_NM') or updated_user.get('nickname')
        if updated_user.get('PROFILE_URL') or updated_user.get('profile_img'):
            session['profile_img'] = updated_user.get('PROFILE_URL') or updated_user.get('profile_img')

    return jsonify({'success': True, 'message': message, 'data': updated_user})

# 4-3. 닉네임 중복 확인 API
@app.route('/api/profile/check_nickname', methods=['GET', 'POST'])
def api_check_nickname():
    data = request.args if request.method == 'GET' else (request.json or {})
    user_id = (data.get('user_id') or session.get('user_id') or request.cookies.get('pst_user_id') or '').strip()
    nickname = (data.get('nickname') or '').strip()
    
    if not nickname:
        return jsonify({'success': False, 'available': False, 'message': '검사할 닉네임을 입력해주세요.'}), 400

    conn = service.get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT NK_NM FROM PST_USER WHERE USER_ID = %s OR LOWER(USER_ID) = LOWER(%s)", (user_id, user_id))
                r = cur.fetchone()
                if r and r.get('NK_NM') and str(r.get('NK_NM')).strip().lower() == nickname.lower():
                    conn.close()
                    return jsonify({'success': True, 'available': True, 'message': '현재 사용 중인 본인의 닉네임입니다.'})
            conn.close()
        except Exception:
            if conn:
                try: conn.close()
                except Exception: pass
        
    is_taken = service.is_nickname_taken(nickname, exclude_user_id=user_id)
    if is_taken:
        return jsonify({'success': True, 'available': False, 'message': '이미 사용 중인 닉네임입니다. 다른 닉네임을 입력해주세요.'})
    else:
        return jsonify({'success': True, 'available': True, 'message': '사용 가능한 닉네임입니다.'})



# 5. 배치 & 관리자 (회차 종료 및 수상자 선정 배치 시뮬레이션)
@app.route('/admin')
def admin():
    return render_template('admin.html', contests=service.get_contests(), winners=service.winners)

# --- API Endpoints ---

@app.route('/api/post/event', methods=['POST'])
def post_event():
    """ 실시간 점수 증가 API (조회 +1, 좋아요 +5, 댓글 +10) """
    try:
        data = request.get_json() or {}
        post_id = data.get('post_id')
        event_type = data.get('event_type') # view, like, comment
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': '로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'require_login': True}), 401

        if not post_id or not event_type:
            return jsonify({'success': False, 'message': '잘못된 요청입니다.'}), 200

        user_id = get_current_user_id()
        
        res = service.trigger_event(post_id, event_type, user_id=user_id)
        if res:
            return jsonify({'success': True, 'data': res})
        return jsonify({'success': False, 'message': '게시물을 찾을 수 없습니다.'}), 200
    except Exception as e:
        print("post_event 오류:", e)
        return jsonify({'success': False, 'message': f'이벤트 처리 중 오류: {str(e)}'}), 200

@app.route('/api/post/delete', methods=['POST'])
def delete_post_entry():
    """ 출전물 삭제 (출전 포기) API """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'message': '로그인이 필요합니다. 먼저 로그인해 주세요! 🐾', 'require_login': True}), 401

        data = request.get_json() or {}
        post_id = data.get('post_id')
        if not post_id:
            return jsonify({'success': False, 'message': '게시물 식별자(post_id)가 필요합니다.'}), 400

        res = service.delete_contest_entry(post_id, user_id)
        return jsonify(res)
    except Exception as e:
        print("delete_post_entry 오류:", e)
        return jsonify({'success': False, 'message': f'출전 포기 처리 중 오류: {str(e)}'}), 500

@app.route('/api/post/user_actions/<path:post_id>', methods=['GET'])
def get_user_post_actions(post_id):
    """ 특정 게시물에 대해 사용자가 4가지 영향력(조회, 좋아요, 댓글, 공유)을 반영했는지 여부 조회 """
    try:
        user_id = get_current_user_id()
        contest_id = 1
        ent_user_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                ent_user_id = parts[1]

        post_detail = service.get_post_detail(contest_id, ent_user_id, current_user_id=user_id)
        actions = post_detail.get('actions', {'is_liked': False, 'is_commented': False}) if post_detail else {'is_liked': False, 'is_commented': False}
        return jsonify({'success': True, 'actions': actions})
    except Exception as e:
        print("user_actions 오류:", e)
        return jsonify({'success': True, 'actions': {'is_viewed': False, 'is_liked': False, 'is_commented': False, 'is_shared': False}})

@app.route('/api/post/liked_status/<path:post_id>', methods=['GET'])
def get_post_liked_status(post_id):
    """ 특정 게시물에 대해 사용자가 좋아요를 눌렀는지 여부 조회 """
    try:
        user_id = session.get('user_id')
        contest_id = 1
        ent_user_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                ent_user_id = parts[1]

        post_detail = service.get_post_detail(contest_id, ent_user_id, current_user_id=user_id)
        actions = post_detail.get('actions', {'is_liked': False, 'is_commented': False}) if post_detail else {'is_liked': False, 'is_commented': False}
        is_liked = actions.get('is_liked', False)
        return jsonify({'success': True, 'is_liked': is_liked, 'actions': actions})
    except Exception as e:
        print("liked_status 오류:", e)
        return jsonify({'success': True, 'is_liked': False})

def process_paw_images_dual(src_file_or_path, contest_id, post_id):
    """
    1. 저장 폴더 : /static/image/contest/yyyy/mm/
    2. 목록용 전체경로 (PHT_FILE_PATH1) : /static/image/contest/yyyy/mm/[CONTEST_ID]_[UUID]_1.webp
    3. 팝업용 전체경로 (PHT_FILE_PATH2) : /static/image/contest/yyyy/mm/[CONTEST_ID]_[UUID]_2.webp
    """
    now = datetime.datetime.now()
    yyyy = now.strftime('%Y')
    mm = now.strftime('%m')
    
    file_dir = f"/static/image/contest/{yyyy}/{mm}/"
    perm_dir = os.path.join(PERM_CONTEST_BASE_DIR, yyyy, mm)
    os.makedirs(perm_dir, exist_ok=True)

    file_uuid = uuid.uuid4().hex[:12]
    list_file_name = f"{contest_id}_{file_uuid}_1.webp"
    popup_file_name = f"{contest_id}_{file_uuid}_2.webp"

    perm_list_path = os.path.join(perm_dir, list_file_name)
    perm_popup_path = os.path.join(perm_dir, popup_file_name)

    temp_filepath = None
    src_img_path = None

    if hasattr(src_file_or_path, 'save'):
        temp_filename = f"temp_{uuid.uuid4().hex[:10]}.tmp"
        temp_filepath = os.path.join(TEMP_CONTEST_DIR, temp_filename)
        src_file_or_path.save(temp_filepath)
        src_img_path = temp_filepath
    elif isinstance(src_file_or_path, str):
        fname = os.path.basename(src_file_or_path)
        temp_filepath = os.path.join(TEMP_CONTEST_DIR, fname)
        if os.path.exists(temp_filepath):
            src_img_path = temp_filepath
        elif os.path.exists(src_file_or_path):
            src_img_path = src_file_or_path

    try:
        if src_img_path and os.path.exists(src_img_path):
            with Image.open(src_img_path) as img:
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img_base = img.convert('RGBA')
                else:
                    img_base = img.convert('RGB')
                
                # 1. 목록용 리사이즈 (max 600x600)
                img_list = img_base.copy()
                img_list.thumbnail((600, 600), Image.Resampling.LANCZOS)
                img_list.save(perm_list_path, 'WEBP', quality=85)

                # 2. 팝업용 리사이즈 (max 1200x1200)
                img_popup = img_base.copy()
                img_popup.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                img_popup.save(perm_popup_path, 'WEBP', quality=92)
    except Exception as e:
        print("process_paw_images_dual error:", e)
    finally:
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass

    full_path1 = f"{file_dir}{list_file_name}"
    full_path2 = f"{file_dir}{popup_file_name}"
    return full_path1, full_path2

@app.route('/api/comments/<path:post_id>', methods=['GET'])
def get_comments(post_id):
    """ 게시물 한줄 댓글 목록 조회 """
    try:
        contest_id = 1
        ent_user_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                ent_user_id = parts[1]

        user_id = session.get('user_id')
        post_detail = service.get_post_detail(contest_id, ent_user_id, user_id)
        comments = post_detail.get('comments', []) if post_detail else []
        return jsonify({'success': True, 'comments': comments})
    except Exception as e:
        print("댓글 조회 오류:", e)
        return jsonify({'success': True, 'comments': []})

@app.route('/api/comments/<path:post_id>', methods=['POST'])
def add_comment_api(post_id):
    """ 한줄 댓글 등록 """
    try:
        data = request.get_json() or {}
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'success': False, 'message': '댓글 내용을 입력해주세요.'}), 200

        user_id = session.get('user_id') or 'guest'

        contest_id = 1
        ent_user_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                ent_user_id = parts[1]

        res = service.add_comment(contest_id, ent_user_id, user_id, content)
        if not res.get('success'):
            return jsonify({
                'success': False,
                'is_author': res.get('is_author', False),
                'message': res.get('message', '댓글 등록 중 오류가 발생했습니다.')
            }), 200

        post_detail = service.get_post_detail(contest_id, ent_user_id)
        comments = post_detail.get('comments', []) if post_detail else []
        latest_comment = comments[-1] if comments else {'CONTS': content}

        vw_cnt = res.get('view_count', post_detail.get('VW_CNT', 0) if post_detail else 0)
        like_cnt = res.get('like_count', post_detail.get('LIKE_CNT', 0) if post_detail else 0)
        cmt_cnt = res.get('comment_count', post_detail.get('CMT_CNT', 0) if post_detail else 0)
        final_score = res.get('score', post_detail.get('SCORE', 0) if post_detail else 0)

        event_res = {
            'view_count': vw_cnt,
            'like_count': like_cnt,
            'comment_count': cmt_cnt,
            'score': final_score,
            'new_score': final_score
        }

        return jsonify({
            'success': True,
            'comment': latest_comment,
            'comments': comments,
            'view_count': vw_cnt,
            'like_count': like_cnt,
            'comment_count': cmt_cnt,
            'score': final_score,
            'new_score': final_score,
            'stats': event_res,
            'event_res': event_res,
            'message': '댓글이 성공적으로 작성되었습니다!'
        })
    except Exception as e:
        print("댓글 등록 오류:", e)
        return jsonify({'success': False, 'message': f'댓글 등록 중 오류: {str(e)}'}), 500

@app.route('/api/comments/<path:post_id>/delete', methods=['POST', 'DELETE'])
def delete_comment_api(post_id):
    """ 한줄 댓글 삭제 """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '로그인이 필요합니다.', 'require_login': True}), 401

        data = request.get_json() or {}
        target_cmt_user_id = data.get('cmt_user_id') or user_id

        contest_id = 1
        ent_user_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                ent_user_id = parts[1]

        res = service.delete_comment(contest_id, ent_user_id, target_cmt_user_id)
        if not res.get('success'):
            return jsonify({'success': False, 'message': res.get('message', '댓글 삭제 중 오류가 발생했습니다.')}), 400

        post_detail = service.get_post_detail(contest_id, ent_user_id, user_id)
        comments = post_detail.get('comments', []) if post_detail else []

        vw_cnt = res.get('view_count', post_detail.get('VW_CNT', 0) if post_detail else 0)
        like_cnt = res.get('like_count', post_detail.get('LIKE_CNT', 0) if post_detail else 0)
        cmt_cnt = res.get('comment_count', post_detail.get('CMT_CNT', 0) if post_detail else 0)
        final_score = res.get('score', post_detail.get('SCORE', 0) if post_detail else 0)

        event_res = {
            'view_count': vw_cnt,
            'like_count': like_cnt,
            'comment_count': cmt_cnt,
            'score': final_score,
            'new_score': final_score
        }

        return jsonify({
            'success': True,
            'message': '댓글이 삭제되었습니다.',
            'comments': comments,
            'view_count': vw_cnt,
            'like_count': like_cnt,
            'comment_count': cmt_cnt,
            'score': final_score,
            'new_score': final_score,
            'stats': event_res,
            'event_res': event_res
        })
    except Exception as e:
        print("댓글 삭제 오류:", e)
        return jsonify({'success': False, 'message': f'댓글 삭제 중 오류: {str(e)}'}), 500

from PIL import Image

TEMP_CONTEST_DIR = os.path.join(app.root_path, 'static', 'image', 'temp', 'contest')
PERM_CONTEST_BASE_DIR = os.path.join(app.root_path, 'static', 'image', 'contest')

os.makedirs(TEMP_CONTEST_DIR, exist_ok=True)
os.makedirs(PERM_CONTEST_BASE_DIR, exist_ok=True)

@app.route('/api/post/upload-temp', methods=['POST'])
def upload_temp_image():
    """ 출전 신청 페이지에서 파일 선택 시 일단 임시 폴더(static/image/temp/contest/)에 임시 저장 """
    try:
        file = request.files.get('media_file') or request.files.get('file') or request.files.get('image')
        if not file or not file.filename:
            return jsonify({'success': False, 'message': '첨부된 이미지 파일이 없습니다.'}), 400

        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        if not ext or len(ext) > 5:
            ext = '.jpg'
        
        temp_filename = f"temp_{uuid.uuid4().hex[:10]}{ext}"
        temp_filepath = os.path.join(TEMP_CONTEST_DIR, temp_filename)
        file.save(temp_filepath)

        temp_url = f"/static/image/temp/contest/{temp_filename}"
        return jsonify({
            'success': True,
            'temp_url': temp_url,
            'temp_filename': temp_filename
        })
    except Exception as e:
        print("임시 업로드 오류:", e)
        return jsonify({'success': False, 'message': f'임시 업로드 실패: {str(e)}'}), 500

@app.route('/api/post/create', methods=['POST'])
def create_post():
    """ 신규 자랑 게시물 등록 API (목록용/팝업용 2개 WebP 생성 & 3개 컬럼 DB 저장) """
    try:
        curr_contest = service.get_current_contest()
        default_cid = (curr_contest.get('CONTEST_ROUND') or curr_contest.get('contest_id') or 13) if curr_contest else 13

        if request.content_type and 'multipart/form-data' in request.content_type:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            pet_name = request.form.get('pet_name', '강아지').strip()
            pet_type = request.form.get('pet_type', '🐕 강아지').strip()
            cid_raw = request.form.get('contest_id')
            contest_id = int(cid_raw) if (cid_raw and str(cid_raw).isdigit()) else default_cid
            user_id = session.get('user_id') or request.form.get('user_id', 'user1')
            temp_filename = request.form.get('temp_filename') or request.form.get('temp_url')
            file = request.files.get('media_file') or request.files.get('file') or request.files.get('image')
            sns_inst = (request.form.get('sns_inst') or '').strip()
            sns_ytb = (request.form.get('sns_ytb') or '').strip()
            sns_fsb = (request.form.get('sns_fsb') or '').strip()
            sns_blg = (request.form.get('sns_blg') or '').strip()
        else:
            data = request.get_json() or {}
            cid_raw = data.get('contest_id')
            contest_id = int(cid_raw) if (cid_raw and str(cid_raw).isdigit()) else default_cid
            user_id = session.get('user_id') or data.get('user_id', 'user1')
            pet_name = data.get('pet_name', '강아지')
            pet_type = data.get('pet_type', '🐕 강아지')
            title = data.get('title', '')
            content = data.get('content', '')
            temp_filename = data.get('temp_filename') or data.get('temp_url')
            file = None
            sns_inst = (data.get('sns_inst') or '').strip()
            sns_ytb = (data.get('sns_ytb') or '').strip()
            sns_fsb = (data.get('sns_fsb') or '').strip()
            sns_blg = (data.get('sns_blg') or '').strip()

        next_post_id = service.get_next_post_id()

        if not pet_type:
            return jsonify({'success': False, 'message': '🐾 반려동물 종류를 선택해 주세요.'}), 400
        if not pet_name:
            return jsonify({'success': False, 'message': '🐶 반려동물 이름을 입력해 주세요.'}), 400
        if not title:
            return jsonify({'success': False, 'message': '✨ 자랑 제목을 입력해 주세요.'}), 400
        if len(title) > 80:
            return jsonify({'success': False, 'message': '✨ 자랑 제목은 80자 이내로 입력해 주세요.'}), 400
        if sns_inst and len(sns_inst) > 200:
            return jsonify({'success': False, 'message': '🔗 인스타그램 주소는 200자 이내로 입력해 주세요.'}), 400
        if sns_ytb and len(sns_ytb) > 200:
            return jsonify({'success': False, 'message': '🔗 유튜브 주소는 200자 이내로 입력해 주세요.'}), 400
        if sns_fsb and len(sns_fsb) > 200:
            return jsonify({'success': False, 'message': '🔗 페이스북 주소는 200자 이내로 입력해 주세요.'}), 400
        if sns_blg and len(sns_blg) > 200:
            return jsonify({'success': False, 'message': '🔗 블로그 주소는 200자 이내로 입력해 주세요.'}), 400

        src_target = temp_filename or file
        if not src_target:
            return jsonify({'success': False, 'message': '🖼️ 출전 사진 파일(이미지)을 첨부해 주세요.'}), 400
        if not content:
            return jsonify({'success': False, 'message': '📝 자랑 내용 및 소개글을 입력해 주세요.'}), 400
        if len(content) > 100:
            return jsonify({'success': False, 'message': '📝 자랑 내용 및 소개글은 100자 이내로 입력해 주세요.'}), 400

        full_path1, full_path2 = process_paw_images_dual(src_target, contest_id, next_post_id)

        new_post = service.create_post(
            contest_id, user_id, pet_name, pet_type, title, content, 
            file_path1=full_path1, file_path2=full_path2, force_post_id=next_post_id,
            sns_inst=sns_inst, sns_ytb=sns_ytb, sns_fsb=sns_fsb, sns_blg=sns_blg
        )
        if isinstance(new_post, dict) and not new_post.get('success'):
            return jsonify({'success': False, 'message': new_post.get('message', '출전 등록에 실패했습니다.')}), 400

        return jsonify({'success': True, 'post': new_post})
    except Exception as e:
        print("게시물 등록 오류:", e)
        return jsonify({'success': False, 'message': f'게시물 등록 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/admin/close-contest', methods=['POST'])
def close_contest():
    """ 배치: 회차 종료 및 수상자 선정 """
    data = request.get_json() or {}
    contest_id = data.get('contest_id')
    if not contest_id:
        return jsonify({'success': False, 'message': '회차 ID가 필요합니다.'}), 400

    new_winners = service.close_contest_and_award(contest_id)
    return jsonify({'success': True, 'winners': new_winners, 'message': f'제{contest_id}회 콘테스트가 성공적으로 종료되었으며 수상자가 선정되었습니다!'})

if __name__ == '__main__':
    print("🐾 Paw Star Server Running on http://127.0.0.1:8003")
    app.run(host='0.0.0.0', port=8003, debug=True)
