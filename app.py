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
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
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
        profile_data = service.get_user_profile(user_id)
        current_user = profile_data.get('user_info', {})
    else:
        current_user = {
            'nickname': '프로필',
            'profile_img': '/static/image/profile/default_profile.png'
        }

    return {
        'contests': service.get_contests(),
        'pet_kinds': service.get_pet_kinds(),
        'app_slogan': '반려동물도 스타가 될 수 있다.',
        'current_user': current_user,
        'is_logged_in': is_logged_in
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
        session.clear()
        session['user_id'] = user_id
        session['last_activity'] = datetime.datetime.now().timestamp()
        session.pop('logged_out', None)
        return jsonify({'success': True, 'message': f'{result["nickname"]}님 환영합니다!', 'user': result})
    else:
        return jsonify({'success': False, 'message': result}), 401

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

    session.clear()
    session['user_id'] = user_id
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({'success': True, 'message': '회원가입이 완료되었습니다!', 'user': new_user})

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


    session.clear()
    session['user_id'] = auto_uuid
    session['has_setup'] = True
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({
        'success': True,
        'message': f'프로필 설정 및 회원가입이 성공적으로 완료되었습니다!',
        'auth_code': password,
        'user': new_user
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

def get_google_config():
    load_env_file()
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '253326907225-2d7t3ics5u6ua4l9bo8hojseuq3u8pqk.apps.googleusercontent.com')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8003/auth/google/callback')
    return client_id, client_secret, redirect_uri

GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI = get_google_config()

@app.route('/auth/google')
def auth_google_redirect():
    """ 팝업 창을 구글 공식 OAuth 2.0 Authorization Code 인증 페이지로 직접 리다이렉트 (response_type=code) """
    next_url = request.args.get('next') or request.args.get('return_url') or '/'
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
        return render_template('google_callback.html', success=True, message=msg, user=user_info, target_url=saved_next_url)
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
        'user': user_info
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

    winners = service.get_hall_of_fame(contest_id=contest_id)
    if winners and winners[0].get('CONTEST_ROUND'):
        w_round = winners[0].get('CONTEST_ROUND')
        if any((c.get('CONTEST_ROUND') == w_round or c.get('contest_id') == w_round) for c in contests):
            contest_id = w_round

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

    user_id = request.args.get('user_id') or session.get('user_id') or 'user1'
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
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=12, user_id=current_user_id)

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

    winners = service.get_hall_of_fame(contest_id=contest_id)
    if winners and winners[0].get('CONTEST_ROUND'):
        w_round = winners[0].get('CONTEST_ROUND')
        if any((c.get('CONTEST_ROUND') == w_round or c.get('contest_id') == w_round) for c in contests):
            contest_id = w_round

    current_contest = service.get_contest(contest_id) if (contest_id and any((c.get('CONTEST_ROUND') == contest_id or c.get('contest_id') == contest_id) for c in contests)) else (contests[0] if contests else None)

    return render_template(
        'm_hall_of_fame.html',
        contests=contests,
        current_contest=current_contest,
        winners=winners
    )

@app.route('/m/profile')
def m_profile():
    user_id = request.args.get('user_id') or session.get('user_id') or 'user1'
    contest_id = request.args.get('contest_id', 'all')
    profile_data = service.get_user_profile(user_id, contest_id=contest_id)

    return render_template(
        'm_profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=profile_data['my_posts'],
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
    user_id = session.get('user_id')
    if not user_id:
        if request.method == 'POST' or request.is_json:
            return jsonify({'success': False, 'message': '로그인이 필요한 서비스입니다. 먼저 로그인해주세요!', 'require_login': True}), 401
        return redirect('/auth/google?next=/upload')

    contests = service.get_contests()
    current_contest = service.get_current_contest() or (contests[0] if contests else None)
    
    if request.method == 'POST':
        contest_id = current_contest['contest_id'] if current_contest else 1
        user_id = session.get('user_id')
        pet_name = request.form.get('pet_name', '우리 아이')
        pet_type = request.form.get('pet_type', '🐕 강아지')
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        media_url = ''
        if 'media_file' in request.files and request.files['media_file'].filename != '':
            uploaded_url = save_uploaded_media(request.files['media_file'])
            if uploaded_url:
                media_url = uploaded_url

        if not media_url:
            media_url = 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80'

        if not title:
            return redirect('/upload')

        service.create_post(contest_id, user_id, pet_name, pet_type, title, content, media_url)
        return redirect('/profile')

    contest_id = current_contest.get('CONTEST_ROUND', 1) if current_contest else 1
    my_entry_count = service.get_user_contest_entry_count(contest_id, user_id)
    remaining_entry_count = max(0, 5 - my_entry_count)
    return render_template(
        'upload.html', 
        current_contest=current_contest, 
        contests=contests,
        my_entry_count=my_entry_count,
        remaining_entry_count=remaining_entry_count,
        pet_kinds=service.get_pet_kinds()
    )

@app.route('/m/upload', methods=['GET', 'POST'])
def m_upload_page():
    user_id = session.get('user_id')
    if not user_id:
        if request.method == 'POST' or request.is_json:
            return jsonify({'success': False, 'message': '로그인이 필요한 서비스입니다. 먼저 로그인해주세요!', 'require_login': True}), 401
        return redirect('/auth/google?next=/m/upload')

    contests = service.get_contests()
    current_contest = service.get_current_contest() or (contests[0] if contests else None)

    if request.method == 'POST':
        contest_id = current_contest.get('CONTEST_ROUND', 1) if current_contest else 1
        user_id = session.get('user_id') or 'user1'
        pet_name = request.form.get('pet_name', '우리 아이')
        pet_type = request.form.get('pet_type', '🐕 강아지')
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        media_url = ''
        if 'media_file' in request.files and request.files['media_file'].filename != '':
            uploaded_url = save_uploaded_media(request.files['media_file'])
            if uploaded_url:
                media_url = uploaded_url

        if not media_url:
            media_url = 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80'

        if not title:
            return redirect('/m/upload')

        service.create_post(contest_id, user_id, pet_name, pet_type, title, content, media_url)
        return redirect('/m/profile')

    contest_id = current_contest.get('CONTEST_ROUND', 1) if current_contest else 1
    my_entry_count = service.get_user_contest_entry_count(contest_id, user_id)
    remaining_entry_count = max(0, 5 - my_entry_count)
    return render_template(
        'm_upload.html', 
        current_contest=current_contest, 
        contests=contests,
        my_entry_count=my_entry_count,
        remaining_entry_count=remaining_entry_count,
        pet_kinds=service.get_pet_kinds()
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

# 4-2. 프로필 수정 API
@app.route('/api/profile/update', methods=['POST'])
def api_profile_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'require_login': True}), 401
    data = request.json or {}
    nickname = data.get('nickname')
    profile_img = data.get('profile_img')
    updated_user = service.update_user_profile(user_id=user_id, nickname=nickname, profile_img=profile_img)
    return jsonify({'success': True, 'message': '프로필 정보가 수정되었습니다.', 'data': updated_user})



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
        return jsonify({'success': True, 'actions': {'is_viewed': True, 'is_liked': False, 'is_commented': False, 'is_shared': False}})

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
    1. 저장 폴더 : /static/image/paw/yyyy/mm/
    2. 목록용 전체경로 (PHT_FILE_PATH1) : /static/image/paw/yyyy/mm/[CONTEST_ID]_[UUID]_1.webp
    3. 팝업용 전체경로 (PHT_FILE_PATH2) : /static/image/paw/yyyy/mm/[CONTEST_ID]_[UUID]_2.webp
    """
    now = datetime.datetime.now()
    yyyy = now.strftime('%Y')
    mm = now.strftime('%m')
    
    file_dir = f"/static/image/paw/{yyyy}/{mm}/"
    perm_dir = os.path.join(PERM_PAW_BASE_DIR, yyyy, mm)
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
        temp_filepath = os.path.join(TEMP_PAW_DIR, temp_filename)
        src_file_or_path.save(temp_filepath)
        src_img_path = temp_filepath
    elif isinstance(src_file_or_path, str):
        fname = os.path.basename(src_file_or_path)
        temp_filepath = os.path.join(TEMP_PAW_DIR, fname)
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
            return jsonify({'success': False, 'message': '댓글 내용을 입력해주세요.'}), 400

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
            return jsonify({'success': False, 'message': res.get('message', '댓글 등록 중 오류가 발생했습니다.')}), 400

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

TEMP_PAW_DIR = os.path.join(app.root_path, 'static', 'image', 'temp', 'paw')
PERM_PAW_BASE_DIR = os.path.join(app.root_path, 'static', 'image', 'paw')

os.makedirs(TEMP_PAW_DIR, exist_ok=True)
os.makedirs(PERM_PAW_BASE_DIR, exist_ok=True)

@app.route('/api/post/upload-temp', methods=['POST'])
def upload_temp_image():
    """ 출전 신청 페이지에서 파일 선택 시 일단 임시 폴더(static/image/temp/paw/)에 임시 저장 """
    try:
        file = request.files.get('media_file') or request.files.get('file') or request.files.get('image')
        if not file or not file.filename:
            return jsonify({'success': False, 'message': '첨부된 이미지 파일이 없습니다.'}), 400

        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        if not ext or len(ext) > 5:
            ext = '.jpg'
        
        temp_filename = f"temp_{uuid.uuid4().hex[:10]}{ext}"
        temp_filepath = os.path.join(TEMP_PAW_DIR, temp_filename)
        file.save(temp_filepath)

        temp_url = f"/static/image/temp/paw/{temp_filename}"
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
        if request.content_type and 'multipart/form-data' in request.content_type:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            pet_name = request.form.get('pet_name', '강아지').strip()
            pet_type = request.form.get('pet_type', '🐕 강아지').strip()
            contest_id = int(request.form.get('contest_id', 3))
            user_id = session.get('user_id') or request.form.get('user_id', 'user1')
            temp_filename = request.form.get('temp_filename') or request.form.get('temp_url')
            file = request.files.get('media_file') or request.files.get('file') or request.files.get('image')
        else:
            data = request.get_json() or {}
            contest_id = int(data.get('contest_id', 3))
            user_id = session.get('user_id') or data.get('user_id', 'user1')
            pet_name = data.get('pet_name', '강아지')
            pet_type = data.get('pet_type', '🐕 강아지')
            title = data.get('title', '')
            content = data.get('content', '')
            temp_filename = data.get('temp_filename') or data.get('temp_url')
            file = None

        next_post_id = service.get_next_post_id()

        if not pet_name:
            return jsonify({'success': False, 'message': '반려동물 이름을 입력해주세요.'}), 400
        if not pet_type:
            return jsonify({'success': False, 'message': '반려동물 종류를 선택해주세요.'}), 400
        if not title:
            return jsonify({'success': False, 'message': '자랑 제목을 입력해주세요.'}), 400
        if not content:
            return jsonify({'success': False, 'message': '자랑 내용 및 소개글을 입력해주세요.'}), 400

        src_target = temp_filename or file
        if not src_target:
            return jsonify({'success': False, 'message': '출전시킬 반려동물 사진 이미지 파일을 반드시 첨부해주세요.'}), 400

        full_path1, full_path2 = process_paw_images_dual(src_target, contest_id, next_post_id)

        new_post = service.create_post(
            contest_id, user_id, pet_name, pet_type, title, content, 
            file_path1=full_path1, file_path2=full_path2, force_post_id=next_post_id
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
