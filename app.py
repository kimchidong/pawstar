"""
Paw Star - Python Flask Web Application
슬로건: "반려동물도 스타가 될 수 있다."
"""

import os
import datetime
import uuid
import shutil
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
from services.contest_service import service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pawstar_secret_key_2026'

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
    """ 30분 동안 웹 서비스 이용(요청)이 없거나 세션 만료 시 자동 로그아웃 처리 """
    now_ts = datetime.datetime.now().timestamp()
    last_act = session.get('last_activity')

    if session.get('user_id') and last_act:
        if now_ts - last_act > 1800:
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
    bio = data.get('bio', '').strip()

    if not user_id or not nickname or not password:
        return jsonify({'success': False, 'message': '아이디, 닉네임, 사용자인증번호(비밀번호)는 필수 입력 사항입니다.'}), 400

    if user_id in service.users:
        return jsonify({'success': False, 'message': '이미 사용 중인 아이디입니다.'}), 400

    # 임시 이미지 디렉터리에 있으면 최종 static/image/profile/YYYY/MM 으로 이동
    if profile_img:
        profile_img = finalize_temp_profile_image(profile_img)

    new_user = service.register_user(user_id, nickname, password, profile_img, bio)

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
    bio = data.get('bio', '').strip()

    if not nickname:
        return jsonify({'success': False, 'message': '집사 닉네임을 입력해주세요.'}), 400

    if not password:
        return jsonify({'success': False, 'message': '로그인 시 사용할 사용자인증번호를 직접 입력해주세요.'}), 400

    auto_uuid = f"user_{uuid.uuid4().hex[:8]}"

    if profile_img:
        profile_img = finalize_temp_profile_image(profile_img)

    new_user = service.register_user(auto_uuid, nickname, password, profile_img, bio)

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

@app.route('/api/auth/google', methods=['POST'])
def api_auth_google():
    """ 구글 인증 전용 로그인 & 회원가입 API (프로필 이미지/닉네임은 사이트 직접 관리) """
    data = request.json or {}
    google_id = data.get('google_id') or data.get('sub') or f"g_{uuid.uuid4().hex[:8]}"
    email = data.get('email', '')
    name = data.get('name', '')

    user_info = service.google_login_or_register(google_id, email, name)

    session.clear()
    session['user_id'] = user_info['user_id']
    session['is_logged_in'] = True
    session['last_activity'] = datetime.datetime.now().timestamp()
    session.pop('logged_out', None)

    return jsonify({
        'success': True,
        'message': f'{user_info["nickname"]}님, Google 계정 인증으로 로그인되었습니다!',
        'user': user_info
    })



def is_mobile_user_agent():
    """ 클라이언트 User-Agent를 판별하여 모바일 기기 접속 여부 반환 """
    ua = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone', 'opera mini']
    return any(k in ua for k in mobile_keywords)

# --- PC 전용 라우트 (1280px 고정) ---

# 1. 홈 (콘테스트 게시물 메인)
@app.route('/')
def index():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_index', **request.args))

    contest_id = request.args.get('contest_id', 3, type=int)
    sort_type = request.args.get('sort', 'latest') # latest(최신등록순), popular(인기순), trending(최근급상승)
    search_q = request.args.get('q', '')
    pet_type = request.args.get('pet_type', 'all')
    page = request.args.get('page', 1, type=int)

    current_contest = service.get_contest(contest_id)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=12)

    return render_template(
        'index.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res,
        sort_type=sort_type,
        search_q=search_q,
        pet_type=pet_type
    )

# 2. 명예의 전당 (Hall of Fame)
@app.route('/hall-of-fame')
def hall_of_fame():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_hall_of_fame', **request.args))

    contest_id = request.args.get('contest_id', 2, type=int)
    current_contest = service.get_contest(contest_id)
    winners = service.get_hall_of_fame(contest_id=contest_id)

    return render_template(
        'hall_of_fame.html',
        current_contest=current_contest,
        winners=winners
    )

# 3. 최근 급상승 메뉴
@app.route('/trending')
def trending():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_trending', **request.args))

    contest_id = request.args.get('contest_id', 3, type=int)
    page = request.args.get('page', 1, type=int)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type='trending', page=page, per_page=10)
    current_contest = service.get_contest(contest_id)

    return render_template(
        'trending.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res
    )

# 4. 프로필 (plamodelshop 회원관리 방식과 동일)
@app.route('/profile')
def profile():
    if is_mobile_user_agent() and not request.args.get('desktop'):
        return redirect(url_for('m_profile', **request.args))

    user_id = request.args.get('user_id', 'user1')
    profile_data = service.get_user_profile(user_id)

    return render_template(
        'profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=profile_data['my_posts'],
        my_awards=profile_data['my_awards']
    )

# --- 모바일 전용 별도 라우트 (m_ 접두사 템플릿 독립 제공) ---

@app.route('/m/')
@app.route('/m')
def m_index():
    contest_id = request.args.get('contest_id', 3, type=int)
    sort_type = request.args.get('sort', 'latest')
    search_q = request.args.get('q', '')
    pet_type = request.args.get('pet_type', 'all')
    page = request.args.get('page', 1, type=int)

    current_contest = service.get_contest(contest_id)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type=sort_type, search_query=search_q, pet_type=pet_type, page=page, per_page=12)

    return render_template(
        'm_index.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res,
        sort_type=sort_type,
        search_q=search_q,
        pet_type=pet_type
    )

@app.route('/m/hall-of-fame')
def m_hall_of_fame():
    contest_id = request.args.get('contest_id', 2, type=int)
    current_contest = service.get_contest(contest_id)
    winners = service.get_hall_of_fame(contest_id=contest_id)

    return render_template(
        'm_hall_of_fame.html',
        current_contest=current_contest,
        winners=winners
    )

@app.route('/m/trending')
def m_trending():
    contest_id = request.args.get('contest_id', 3, type=int)
    page = request.args.get('page', 1, type=int)
    paginated_res = service.get_posts(contest_id=contest_id, sort_type='trending', page=page, per_page=10)
    current_contest = service.get_contest(contest_id)

    return render_template(
        'm_trending.html',
        current_contest=current_contest,
        posts=paginated_res['posts'],
        pagination=paginated_res
    )

@app.route('/m/profile')
def m_profile():
    user_id = request.args.get('user_id', 'user1')
    profile_data = service.get_user_profile(user_id)

    return render_template(
        'm_profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=profile_data['my_posts'],
        my_awards=profile_data['my_awards']
    )

@app.route('/m/admin')
def m_admin():
    return render_template('m_admin.html', contests=service.get_contests(), winners=service.winners)


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
    data = request.json or {}
    user_id = data.get('user_id', 'user1')
    nickname = data.get('nickname')
    bio = data.get('bio')
    profile_img = data.get('profile_img')

    # 임시 저장 디렉터리에 있는 경우 최종 static/image/profile/YYYY/MM 디렉터리로 이동
    if profile_img:
        profile_img = finalize_temp_profile_image(profile_img)

    updated_user = service.update_user_profile(user_id=user_id, nickname=nickname, bio=bio, profile_img=profile_img)
    return jsonify({'success': True, 'message': '프로필 정보가 수정되었습니다.', 'data': updated_user})


# 5. 배치 & 관리자 (회차 종료 및 수상자 선정 배치 시뮬레이션)
@app.route('/admin')
def admin():
    return render_template('admin.html', contests=service.get_contests(), winners=service.winners)

# --- API Endpoints ---

@app.route('/api/post/event', methods=['POST'])
def post_event():
    """ 실시간 점수 증가 API (조회 +1, 좋아요 +5, 댓글 +10, 공유 +20) """
    data = request.get_json() or {}
    post_id = data.get('post_id')
    event_type = data.get('event_type') # view, like, comment, share

    if not post_id or not event_type:
        return jsonify({'success': False, 'message': '잘못된 요청입니다.'}), 400

    res = service.trigger_event(post_id, event_type)
    if res:
        return jsonify({'success': True, 'data': res})
    return jsonify({'success': False, 'message': '게시물을 찾을 수 없습니다.'}), 404

@app.route('/api/post/create', methods=['POST'])
def create_post():
    """ 신규 자랑 게시물 등록 API """
    data = request.get_json() or {}
    contest_id = data.get('contest_id', 3)
    user_id = data.get('user_id', 'user1')
    pet_name = data.get('pet_name', '우리 아이')
    pet_type = data.get('pet_type', '🐕 강아지')
    title = data.get('title', '')
    content = data.get('content', '')
    media_url = data.get('media_url', '')

    if not title:
        return jsonify({'success': False, 'message': '제목을 입력해주세요.'}), 400

    new_post = service.create_post(contest_id, user_id, pet_name, pet_type, title, content, media_url)
    return jsonify({'success': True, 'post': new_post})

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
