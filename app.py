"""
Paw Star - Python Flask Web Application
슬로건: "반려동물도 스타가 될 수 있다."
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from services.contest_service import service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pawstar_secret_key_2026'

@app.context_processor
def inject_global_vars():
    """ 템플릿 전역에서 사용할 기본 정보 전달 """
    return {
        'contests': service.get_contests(),
        'app_slogan': '반려동물도 스타가 될 수 있다.'
    }

# 1. 홈 (콘테스트 게시물 메인)
@app.route('/')
def index():
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
    user_id = request.args.get('user_id', 'user1')
    profile_data = service.get_user_profile(user_id)

    return render_template(
        'profile.html',
        user=profile_data['user_info'],
        stats=profile_data['stats'],
        my_posts=profile_data['my_posts'],
        my_awards=profile_data['my_awards']
    )

# 4-1. 프로필 수정 API
@app.route('/api/profile/update', methods=['POST'])
def api_profile_update():
    data = request.json or {}
    user_id = data.get('user_id', 'user1')
    nickname = data.get('nickname')
    bio = data.get('bio')
    profile_img = data.get('profile_img')

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
