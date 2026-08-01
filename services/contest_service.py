"""
Paw Star Contest Service (get_posts & get_post_detail query rewrite)
"""

from datetime import datetime, timedelta
import pymysql
from config import db_config

class PawStarService:
    def __init__(self):
        pass

    def get_db_connection(self):
        try:
            return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            print("DB Connection Error:", e)
            return None

    def _attach_d_day(self, contest):
        if not contest:
            return contest
        end_dt = contest.get('ED_DT') or contest.get('end_date')
        if not end_dt:
            contest['d_day_str'] = "상시 진행"
            return contest

        if isinstance(end_dt, str):
            try:
                end_dt = datetime.strptime(end_dt[:10], "%Y-%m-%d")
            except Exception:
                contest['d_day_str'] = "상시 진행"
                return contest

        now = datetime.now()
        diff_days = (end_dt - now).days
        if diff_days < 0:
            contest['d_day_str'] = "종료됨"
        elif diff_days == 0:
            contest['d_day_str'] = "D-DAY Today"
        else:
            contest['d_day_str'] = f"D-{diff_days}"
        return contest

    def get_user_contest_entry_count(self, contest_id, base_user_id):
        conn = self.get_db_connection()
        if not conn:
            return 0
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND (ENT_USER_ID = %s OR ENT_USER_ID LIKE %s)
                """, (contest_id, base_user_id, f"{base_user_id}_post_%"))
                r = cur.fetchone()
                conn.close()
                return r['cnt'] if r else 0
        except Exception as e:
            print("get_user_contest_entry_count error:", e)
            return 0

    def get_next_post_id(self):
        conn = self.get_db_connection()
        if not conn:
            return 1
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) + 1 AS next_id FROM pst_contest_round")
                r = cur.fetchone()
                conn.close()
                return r['next_id'] if r else 1
        except Exception:
            return 1

    def get_pet_kinds(self):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT KIND_CD, KIND_NM, KIND_CLASS FROM pst_pet_kind ORDER BY KIND_CD ASC")
                rows = cur.fetchall()
                conn.close()
                return rows
        except Exception as e:
            print("get_pet_kinds error:", e)
            return []

    def get_contests(self):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.CONTEST_ROUND,
                        c.THEME_CD,
                        t.THEME_NM,
                        t.THEME_MENT,
                        c.ST_DT,
                        c.ED_DT,
                        c.CONTEST_STAT,
                        cd.CD_NM AS CONTEST_STAT_NM,
                        t.THEME_MENT AS CONTS,
                        t.BANNER_IMG_FILE_PATH,
                        c.CONTEST_ROUND AS contest_id,
                        t.THEME_NM AS title,
                        t.THEME_MENT AS description,
                        c.ST_DT AS start_date,
                        c.ED_DT AS end_date,
                        cd.CD_NM AS status,
                        t.BANNER_IMG_FILE_PATH AS banner_img
                    FROM pst_contest c
                    JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    JOIN pst_cd cd ON c.CONTEST_STAT = cd.CD
                    ORDER BY c.CONTEST_ROUND DESC
                """)
                rows = cur.fetchall()
                contests = [self._attach_d_day(r) for r in rows]
                conn.close()
                return contests
        except Exception as e:
            print("get_contests error:", e)
            return []

    def get_closed_contests(self):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.CONTEST_ROUND,
                        c.THEME_CD,
                        t.THEME_NM,
                        t.THEME_MENT,
                        c.ST_DT,
                        c.ED_DT,
                        c.CONTEST_STAT,
                        cd.CD_NM AS CONTEST_STAT_NM,
                        t.THEME_MENT AS CONTS,
                        t.BANNER_IMG_FILE_PATH,
                        c.CONTEST_ROUND AS contest_id,
                        t.THEME_NM AS title,
                        t.THEME_MENT AS description,
                        c.ST_DT AS start_date,
                        c.ED_DT AS end_date,
                        cd.CD_NM AS status
                    FROM pst_contest c
                    JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    JOIN pst_cd cd ON c.CONTEST_STAT = cd.CD
                    WHERE c.CONTEST_STAT = 'G001C002'
                    ORDER BY c.CONTEST_ROUND DESC
                """)
                rows = cur.fetchall()
                contests = [self._attach_d_day(r) for r in rows]
                conn.close()
                return contests
        except Exception as e:
            print("get_closed_contests error:", e)
            return []

    def get_current_contest(self, contest_id=None):
        contests = self.get_contests()
        if not contests:
            return {
                'CONTEST_ROUND': 1,
                'THEME_NM': '한여름 밤의 바캉스',
                'THEME_MENT': '파도 소리와 함께 즐기는 핫한 바캉스! 여름 최고의 슈퍼스타 등장 🌴',
                'ST_DT': '2026-08-01',
                'ED_DT': '2026-08-31',
                'CONTEST_STAT': 'G001C001',
                'CONTEST_STAT_NM': '진행중',
                'CONTS': '파도 소리와 함께 즐기는 핫한 바캉스! 여름 최고의 슈퍼스타 등장 🌴',
                'BANNER_IMG_FILE_PATH': '/static/image/banner/T008.png',
                'd_day_str': 'D-30',
                'contest_id': 1,
                'title': '한여름 밤의 바캉스',
                'description': '파도 소리와 함께 즐기는 핫한 바캉스! 여름 최고의 슈퍼스타 등장 🌴',
                'status': '진행중'
            }

        if contest_id:
            for c in contests:
                if str(c['CONTEST_ROUND']) == str(contest_id) or str(c.get('contest_id')) == str(contest_id):
                    return c

        for c in contests:
            if c.get('CONTEST_STAT_NM') == '진행중' or c.get('status') == '진행중':
                return c

        return contests[0]

    def get_contest(self, contest_id=None):
        return self.get_current_contest(contest_id)

    def is_user_exists(self, user_id):
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pst_user WHERE USER_ID = %s", (user_id,))
                res = bool(cur.fetchone())
                conn.close()
                return res
        except Exception:
            return False

    def register_user(self, user_id, nickname, password="", profile_img="", bio=""):
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pst_user (USER_ID, NK_NM, PROFILE_URL, LGN_CNT, LGN_DT, JOIN_DT)
                    VALUES (%s, %s, %s, 1, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE NK_NM=VALUES(NK_NM), PROFILE_URL=VALUES(PROFILE_URL), LGN_CNT=LGN_CNT+1, LGN_DT=NOW()
                """, (user_id, nickname, profile_img or '/static/image/profile/default_profile.png'))
                conn.commit()
                conn.close()
                return {'USER_ID': user_id, 'NK_NM': nickname, 'PROFILE_URL': profile_img, 'user_id': user_id, 'nickname': nickname, 'profile_img': profile_img}
        except Exception as e:
            print("register_user error:", e)
            return None

    def google_login_or_register(self, google_id, email, name, picture="", **kwargs):
        user_id = f"google_{google_id}" if google_id else (email or "google_user")
        nickname = name or (email.split('@')[0] if email else "구글집사")
        profile_img = picture or '/static/image/profile/default_profile.png'

        conn = self.get_db_connection()
        if not conn:
            return {
                'USER_ID': user_id,
                'NK_NM': nickname,
                'PROFILE_URL': profile_img,
                'user_id': user_id,
                'nickname': nickname,
                'profile_img': profile_img
            }

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT USER_ID, NK_NM, PROFILE_URL FROM pst_user WHERE USER_ID = %s", (user_id,))
                user = cur.fetchone()

                if not user:
                    cur.execute("""
                        INSERT INTO pst_user (USER_ID, NK_NM, PROFILE_URL, LGN_CNT, LGN_DT, JOIN_DT)
                        VALUES (%s, %s, %s, 1, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE LGN_CNT = LGN_CNT + 1, LGN_DT = NOW()
                    """, (user_id, nickname, profile_img))
                    conn.commit()
                    user_info = {
                        'USER_ID': user_id,
                        'NK_NM': nickname,
                        'PROFILE_URL': profile_img,
                        'user_id': user_id,
                        'nickname': nickname,
                        'profile_img': profile_img
                    }
                else:
                    cur.execute("UPDATE pst_user SET LGN_CNT = LGN_CNT + 1, LGN_DT = NOW() WHERE USER_ID = %s", (user_id,))
                    conn.commit()
                    user_info = {
                        'USER_ID': user['USER_ID'],
                        'NK_NM': user.get('NK_NM', nickname),
                        'PROFILE_URL': user.get('PROFILE_URL', profile_img),
                        'user_id': user['USER_ID'],
                        'nickname': user.get('NK_NM', nickname),
                        'profile_img': user.get('PROFILE_URL', profile_img)
                    }

                conn.close()
                return user_info
        except Exception as e:
            print("google_login_or_register error:", e)
            return {
                'USER_ID': user_id,
                'NK_NM': nickname,
                'PROFILE_URL': profile_img,
                'user_id': user_id,
                'nickname': nickname,
                'profile_img': profile_img
            }

    def update_user_profile(self, user_id, nickname, bio="", profile_img="", **kwargs):
        conn = self.get_db_connection()
        if not conn:
            return {
                'USER_ID': user_id,
                'NK_NM': nickname,
                'PROFILE_URL': profile_img or '/static/image/profile/default_profile.png',
                'user_id': user_id,
                'nickname': nickname,
                'profile_img': profile_img or '/static/image/profile/default_profile.png'
            }
        try:
            with conn.cursor() as cur:
                if profile_img:
                    cur.execute("""
                        UPDATE pst_user
                        SET NK_NM = %s, PROFILE_URL = %s
                        WHERE USER_ID = %s OR USER_ID LIKE %s
                    """, (nickname, profile_img, user_id, f"{user_id}_post_%"))
                else:
                    cur.execute("""
                        UPDATE pst_user
                        SET NK_NM = %s
                        WHERE USER_ID = %s OR USER_ID LIKE %s
                    """, (nickname, user_id, f"{user_id}_post_%"))

                conn.commit()

                cur.execute("SELECT USER_ID, NK_NM, PROFILE_URL FROM pst_user WHERE USER_ID = %s", (user_id,))
                user = cur.fetchone()
                conn.close()

                final_nk = user.get('NK_NM', nickname) if user else nickname
                final_img = user.get('PROFILE_URL', profile_img or '/static/image/profile/default_profile.png') if user else (profile_img or '/static/image/profile/default_profile.png')

                return {
                    'USER_ID': user_id,
                    'NK_NM': final_nk,
                    'PROFILE_URL': final_img,
                    'user_id': user_id,
                    'nickname': final_nk,
                    'profile_img': final_img
                }
        except Exception as e:
            print("update_user_profile error:", e)
            return {
                'USER_ID': user_id,
                'NK_NM': nickname,
                'PROFILE_URL': profile_img or '/static/image/profile/default_profile.png',
                'user_id': user_id,
                'nickname': nickname,
                'profile_img': profile_img or '/static/image/profile/default_profile.png'
            }

    def delete_user(self, user_id):
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM pst_contest_round WHERE ENT_USER_ID = %s OR ENT_USER_ID LIKE %s", (user_id, f"{user_id}_post_%"))
                cur.execute("DELETE FROM pst_user WHERE USER_ID = %s OR USER_ID LIKE %s", (user_id, f"{user_id}_post_%"))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print("delete_user error:", e)
            return False

    def get_user_profile(self, user_id):
        conn = self.get_db_connection()
        if not conn:
            return {
                'user_info': {'USER_ID': user_id, 'NK_NM': '프로필', 'PROFILE_URL': '/static/image/profile/default_profile.png', 'user_id': user_id, 'nickname': '프로필', 'profile_img': '/static/image/profile/default_profile.png'},
                'stats': {'my_post_count': 0, 'total_score': 0, 'total_likes': 0, 'award_count': 0},
                'my_posts': [],
                'my_awards': []
            }
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT USER_ID, NK_NM, PROFILE_URL, LGN_CNT, LGN_DT, JOIN_DT
                    FROM pst_user WHERE USER_ID = %s
                """, (user_id,))
                user_info = cur.fetchone()

                if not user_info:
                    user_info = {'USER_ID': user_id, 'NK_NM': user_id, 'PROFILE_URL': '/static/image/profile/default_profile.png'}

                cur.execute("""
                    SELECT 
                        r.CONTEST_ROUND,
                        r.ENT_USER_ID,
                        r.ENT_USER_ID AS USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        k.KIND_NM,
                        k.KIND_CLASS,
                        r.PET_NM,
                        r.TITLE,
                        r.CONTS,
                        r.PHT_PATH,
                        r.PHT_FILE1,
                        r.PHT_FILE2,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN 
                                IF(RIGHT(r.PHT_PATH, 1) = '/', CONCAT(r.PHT_PATH, r.PHT_FILE1), CONCAT(r.PHT_PATH, '/', r.PHT_FILE1))
                            ELSE CONCAT('/static/image/paw/2026/08/', r.PHT_FILE1)
                        END AS IMAGE_PATH,
                        r.VW_CNT,
                        r.LIKE_CNT,
                        r.CMT_CNT,
                        r.SCORE,
                        r.ENT_DT,
                        -- 호환 키
                        r.CONTEST_ROUND AS contest_id,
                        r.ENT_USER_ID AS user_id,
                        CONCAT(r.CONTEST_ROUND, '_', r.ENT_USER_ID) AS post_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        k.KIND_NM AS pet_type,
                        r.PET_NM AS pet_name,
                        r.TITLE AS title,
                        r.CONTS AS content,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN 
                                IF(RIGHT(r.PHT_PATH, 1) = '/', CONCAT(r.PHT_PATH, r.PHT_FILE1), CONCAT(r.PHT_PATH, '/', r.PHT_FILE1))
                            ELSE CONCAT('/static/image/paw/2026/08/', r.PHT_FILE1)
                        END AS image_path,
                        r.VW_CNT AS view_count,
                        r.LIKE_CNT AS like_count,
                        r.CMT_CNT AS comment_count,
                        r.SCORE AS score
                    FROM pst_contest_round r
                    JOIN pst_user u ON SUBSTRING_INDEX(r.ENT_USER_ID, '_post_', 1) = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    WHERE r.ENT_USER_ID = %s OR r.ENT_USER_ID LIKE %s
                    ORDER BY r.ENT_DT DESC
                """, (user_id, f"{user_id}_post_%"))
                my_posts = cur.fetchall()

                for p in my_posts:
                    dt_val = p.get('ENT_DT')
                    if hasattr(dt_val, 'strftime'):
                        dt_str = dt_val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dt_str = str(dt_val or '')
                    p['ENT_DT'] = dt_str
                    p['created_at'] = dt_str

                my_post_count = len(my_posts)
                total_score = sum(p.get('SCORE', 0) for p in my_posts)
                total_likes = sum(p.get('LIKE_CNT', 0) for p in my_posts)

                cur.execute("""
                    SELECT 
                        ca.CONTEST_ROUND, ca.AWARD_CD, a.AWARD_NM, a.BADGE_IMG_PATH_FILE,
                        ca.CONTEST_ROUND AS contest_id, a.AWARD_NM AS prize_name, a.BADGE_IMG_PATH_FILE AS badge_img
                    FROM pst_contest_award ca
                    JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                    WHERE ca.ENT_USER_ID = %s OR ca.ENT_USER_ID LIKE %s
                """, (user_id, f"{user_id}_post_%"))
                my_awards = cur.fetchall()

                conn.close()
                return {
                    'user_info': {
                        'USER_ID': user_info['USER_ID'],
                        'NK_NM': user_info.get('NK_NM', user_id),
                        'PROFILE_URL': user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png'),
                        'user_id': user_info['USER_ID'],
                        'nickname': user_info.get('NK_NM', user_id),
                        'profile_img': user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png')
                    },
                    'stats': {
                        'my_post_count': my_post_count,
                        'total_score': total_score,
                        'total_likes': total_likes,
                        'award_count': len(my_awards)
                    },
                    'my_posts': my_posts,
                    'my_awards': my_awards
                }
        except Exception as e:
            print("get_user_profile error:", e)
            return {
                'user_info': {'USER_ID': user_id, 'NK_NM': user_id, 'PROFILE_URL': '/static/image/profile/default_profile.png', 'user_id': user_id, 'nickname': user_id, 'profile_img': '/static/image/profile/default_profile.png'},
                'stats': {'my_post_count': 0, 'total_score': 0, 'total_likes': 0, 'award_count': 0},
                'my_posts': [],
                'my_awards': []
            }

    def create_contest_entry(self, contest_id, user_id, kind_cd, pet_name, title, content, pht_path, pht_file1, pht_file2=""):
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        
        entry_cnt = self.get_user_contest_entry_count(contest_id, user_id)
        if entry_cnt >= 5:
            return {
                'success': False,
                'message': f'해당 회차에는 회원 1인당 최대 5회까지만 출전이 가능합니다. (현재 {entry_cnt}/5회 출전 완료)'
            }

        actual_ent_user_id = user_id if entry_cnt == 0 else f"{user_id}_post_{entry_cnt + 1}"

        if not self.is_user_exists(user_id):
            self.register_user(user_id, user_id)
        if actual_ent_user_id != user_id and not self.is_user_exists(actual_ent_user_id):
            self.register_user(actual_ent_user_id, user_id)

        if kind_cd and not kind_cd.startswith('K'):
            kinds = self.get_pet_kinds()
            for k in kinds:
                if k['KIND_NM'] in kind_cd or kind_cd in k['KIND_NM']:
                    kind_cd = k['KIND_CD']
                    break
            else:
                kind_cd = 'K008'

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pst_contest_round 
                    (CONTEST_ROUND, ENT_USER_ID, KIND_CD, PET_NM, TITLE, CONTS, PHT_PATH, PHT_FILE1, PHT_FILE2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        KIND_CD=VALUES(KIND_CD), PET_NM=VALUES(PET_NM), TITLE=VALUES(TITLE),
                        CONTS=VALUES(CONTS), PHT_PATH=VALUES(PHT_PATH), PHT_FILE1=VALUES(PHT_FILE1), PHT_FILE2=VALUES(PHT_FILE2)
                """, (contest_id, actual_ent_user_id, kind_cd, pet_name, title, content, pht_path, pht_file1, pht_file2))
                conn.commit()
                conn.close()
                return {'success': True, 'ent_user_id': actual_ent_user_id}
        except Exception as e:
            print("create_contest_entry error:", e)
            return {'success': False, 'message': str(e)}

    def create_post(self, contest_id, user_id, pet_name, pet_type, title, content, media_url="", file_path="", list_file_name="", popup_file_name="", **kwargs):
        pht_path = file_path or "/static/image/post"
        pht_file1 = list_file_name

        if media_url and not pht_file1:
            if "/" in media_url:
                parts = media_url.rsplit('/', 1)
                pht_path = parts[0]
                pht_file1 = parts[1]
            else:
                pht_file1 = media_url

        if not pht_file1:
            pht_file1 = "default_pet.jpg"

        res = self.create_contest_entry(contest_id, user_id, pet_type, pet_name, title, content, pht_path, pht_file1, popup_file_name)
        if not res.get('success'):
            return res

        actual_user_id = res.get('ent_user_id', user_id)
        return {
            'success': True,
            'CONTEST_ROUND': contest_id,
            'ENT_USER_ID': actual_user_id,
            'post_id': f"{contest_id}_{actual_user_id}",
            'PET_NM': pet_name,
            'TITLE': title
        }

    def get_posts(self, contest_id=None, pet_type='all', sort_type='latest', search_q='', search_query='', current_user_id=None, user_id=None, page=1, per_page=12, **kwargs):
        search_q = search_query or search_q
        current_user_id = user_id or current_user_id

        conn = self.get_db_connection()
        if not conn:
            empty_pag = {'total_count': 0, 'page': 1, 'total_pages': 1, 'per_page': per_page}
            return {'posts': [], 'total_count': 0, 'page': 1, 'total_pages': 1, 'per_page': per_page, 'pagination': empty_pag}

        try:
            if not contest_id:
                curr = self.get_current_contest()
                contest_id = curr['CONTEST_ROUND'] if curr else 1

            query = """
                SELECT 
                    r.CONTEST_ROUND,
                    r.ENT_USER_ID,
                    r.ENT_USER_ID AS USER_ID,
                    u.NK_NM,
                    COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                    k.KIND_NM,
                    k.KIND_CLASS,
                    r.PET_NM,
                    r.TITLE,
                    r.CONTS,
                    r.PHT_PATH,
                    r.PHT_FILE1,
                    r.PHT_FILE2,
                    CASE 
                        WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                        ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                    END AS IMAGE_PATH,
                    r.VW_CNT,
                    r.LIKE_CNT,
                    r.CMT_CNT,
                    r.SCORE,
                    r.ENT_DT AS ENT_DT,
                    r.TOTAL_RANKING,
                    r.KIND_RANKING,
                    -- 호환용
                    r.CONTEST_ROUND AS contest_id,
                    r.ENT_USER_ID AS user_id,
                    CONCAT(r.CONTEST_ROUND, '_', r.ENT_USER_ID) AS post_id,
                    u.NK_NM AS user_nickname,
                    COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                    k.KIND_NM AS pet_type,
                    r.PET_NM AS pet_name,
                    r.TITLE AS title,
                    r.CONTS AS content,
                    r.PHT_PATH AS file_path,
                    r.PHT_FILE1 AS list_file_name,
                    CASE 
                        WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                        ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                    END AS image_path,
                    r.VW_CNT AS view_count,
                    r.LIKE_CNT AS like_count,
                    r.CMT_CNT AS comment_count,
                    r.SCORE AS score,
                    r.ENT_DT AS created_at
                FROM pst_contest_round r
                JOIN pst_user u ON SUBSTRING_INDEX(r.ENT_USER_ID, '_post_', 1) = u.USER_ID
                LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                WHERE r.CONTEST_ROUND = %s
            """
            params = [contest_id]

            if pet_type and pet_type != 'all':
                query += " AND (k.KIND_NM LIKE %s OR r.PET_NM LIKE %s)"
                params.extend([f"%{pet_type}%", f"%{pet_type}%"])

            if search_q:
                query += " AND (r.TITLE LIKE %s OR r.CONTS LIKE %s OR r.PET_NM LIKE %s OR u.NK_NM LIKE %s)"
                params.extend([f"%{search_q}%", f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"])

            if sort_type == 'popular':
                query += " ORDER BY r.LIKE_CNT DESC, r.SCORE DESC, r.ENT_DT DESC"
            elif sort_type == 'score':
                query += " ORDER BY r.SCORE DESC, r.ENT_DT DESC"
            else:
                query += " ORDER BY r.ENT_DT DESC"

            with conn.cursor() as cur:
                cur.execute(query, params)
                all_rows = cur.fetchall()

                liked_user_ids = set()
                if current_user_id:
                    cur.execute("""
                        SELECT ENT_USER_ID FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND LIKE_USER_ID = %s
                    """, (contest_id, current_user_id))
                    liked_rows = cur.fetchall()
                    liked_user_ids = {r['ENT_USER_ID'] for r in liked_rows}

                total_count = len(all_rows)
                total_pages = max(1, (total_count + per_page - 1) // per_page)
                page = max(1, min(page, total_pages))
                start_idx = (page - 1) * per_page
                paged_rows = all_rows[start_idx:start_idx + per_page]

                score_sorted = sorted(all_rows, key=lambda x: x['SCORE'], reverse=True)
                top_scores = {r['ENT_USER_ID']: idx + 1 for idx, r in enumerate(score_sorted[:3])}

                posts = []
                for row in paged_rows:
                    dt_val = row.get('ENT_DT')
                    if hasattr(dt_val, 'strftime'):
                        dt_str = dt_val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dt_str = str(dt_val or '')
                    row['ENT_DT'] = dt_str
                    row['created_at'] = dt_str
                    row['rank_candidate'] = top_scores.get(row['ENT_USER_ID'], None)
                    row['actions'] = {'is_liked': row['ENT_USER_ID'] in liked_user_ids}
                    posts.append(row)

                conn.close()

                pag_dict = {
                    'total_count': total_count,
                    'page': page,
                    'total_pages': total_pages,
                    'per_page': per_page
                }

                return {
                    'posts': posts,
                    'total_count': total_count,
                    'page': page,
                    'total_pages': total_pages,
                    'per_page': per_page,
                    'pagination': pag_dict
                }
        except Exception as e:
            print("get_posts error:", e)
            empty_pag = {'total_count': 0, 'page': 1, 'total_pages': 1, 'per_page': per_page}
            return {'posts': [], 'total_count': 0, 'page': 1, 'total_pages': 1, 'per_page': per_page, 'pagination': empty_pag}

    def get_post_detail(self, contest_id, ent_user_id, current_user_id=None):
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        r.CONTEST_ROUND,
                        r.ENT_USER_ID,
                        r.ENT_USER_ID AS USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        k.KIND_NM,
                        k.KIND_CLASS,
                        r.PET_NM,
                        r.TITLE,
                        r.CONTS,
                        r.PHT_PATH,
                        r.PHT_FILE1,
                        r.PHT_FILE2,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                            ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                        END AS IMAGE_PATH,
                        r.VW_CNT,
                        r.LIKE_CNT,
                        r.CMT_CNT,
                        r.SCORE,
                        r.ENT_DT AS ENT_DT,
                        -- 호환용
                        r.CONTEST_ROUND AS contest_id,
                        r.ENT_USER_ID AS user_id,
                        CONCAT(r.CONTEST_ROUND, '_', r.ENT_USER_ID) AS post_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        k.KIND_NM AS pet_type,
                        r.PET_NM AS pet_name,
                        r.TITLE AS title,
                        r.CONTS AS content,
                        r.PHT_PATH AS file_path,
                        r.PHT_FILE1 AS list_file_name,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                            ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                        END AS image_path,
                        r.VW_CNT AS view_count,
                        r.LIKE_CNT AS like_count,
                        r.CMT_CNT AS comment_count,
                        r.SCORE AS score,
                        r.ENT_DT AS created_at
                    FROM pst_contest_round r
                    JOIN pst_user u ON SUBSTRING_INDEX(r.ENT_USER_ID, '_post_', 1) = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    WHERE r.CONTEST_ROUND = %s AND r.ENT_USER_ID = %s
                """, (contest_id, ent_user_id))
                post = cur.fetchone()
                if not post:
                    conn.close()
                    return None

                cur.execute("""
                    SELECT 
                        c.CMT_USER_ID AS USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        c.CMT AS CONTS,
                        c.CMD_DT AS CMD_DT,
                        -- 호환용
                        c.CMT_USER_ID AS user_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        c.CMT AS content,
                        c.CMD_DT AS created_at
                    FROM pst_contest_cmt c
                    JOIN pst_user u ON SUBSTRING_INDEX(c.CMT_USER_ID, '_post_', 1) = u.USER_ID
                    WHERE c.CONTEST_ROUND = %s AND c.ENT_USER_ID = %s
                    ORDER BY c.CMD_DT ASC
                """, (contest_id, ent_user_id))
                comments = cur.fetchall()

                is_liked = False
                if current_user_id:
                    cur.execute("""
                        SELECT 1 FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s AND LIKE_USER_ID = %s
                    """, (contest_id, ent_user_id, current_user_id))
                    is_liked = bool(cur.fetchone())

                dt_p = post.get('ENT_DT')
                if hasattr(dt_p, 'strftime'):
                    p_str = dt_p.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    p_str = str(dt_p or '')
                post['ENT_DT'] = p_str
                post['created_at'] = p_str

                cmt_list = []
                for c in comments:
                    dt_c = c.get('CMD_DT')
                    if hasattr(dt_c, 'strftime'):
                        c_str = dt_c.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        c_str = str(dt_c or '')
                    c['CMD_DT'] = c_str
                    c['created_at'] = c_str
                    cmt_list.append(c)

                post['comments'] = cmt_list
                post['actions'] = {'is_liked': is_liked}
                conn.close()
                return post
        except Exception as e:
            print("get_post_detail error:", e)
            return None

    def increase_view_count(self, contest_id, ent_user_id, view_user_id=None):
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                if view_user_id:
                    cur.execute("""
                        INSERT IGNORE INTO pst_contest_vw (CONTEST_ROUND, ENT_USER_ID, VW_USER_ID)
                        VALUES (%s, %s, %s)
                    """, (contest_id, ent_user_id, view_user_id))

                cur.execute("""
                    UPDATE pst_contest_round
                    SET VW_CNT = VW_CNT + 1, SCORE = SCORE + 1
                    WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                """, (contest_id, ent_user_id))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print("increase_view_count error:", e)
            return False

    def toggle_like(self, contest_id, ent_user_id, like_user_id):
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM pst_contest_like
                    WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s AND LIKE_USER_ID = %s
                """, (contest_id, ent_user_id, like_user_id))
                exists = cur.fetchone()

                if exists:
                    cur.execute("""
                        DELETE FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s AND LIKE_USER_ID = %s
                    """, (contest_id, ent_user_id, like_user_id))
                    cur.execute("""
                        UPDATE pst_contest_round
                        SET LIKE_CNT = GREATEST(0, LIKE_CNT - 1), SCORE = GREATEST(0, SCORE - 5)
                        WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                    """, (contest_id, ent_user_id))
                    is_liked = False
                else:
                    cur.execute("""
                        INSERT INTO pst_contest_like (CONTEST_ROUND, ENT_USER_ID, LIKE_USER_ID)
                        VALUES (%s, %s, %s)
                    """, (contest_id, ent_user_id, like_user_id))
                    cur.execute("""
                        UPDATE pst_contest_round
                        SET LIKE_CNT = LIKE_CNT + 1, SCORE = SCORE + 5
                        WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                    """, (contest_id, ent_user_id))
                    is_liked = True

                conn.commit()
                cur.execute("SELECT LIKE_CNT FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s", (contest_id, ent_user_id))
                r = cur.fetchone()
                like_count = r['LIKE_CNT'] if r else 0

                conn.close()
                return {'success': True, 'is_liked': is_liked, 'like_count': like_count}
        except Exception as e:
            print("toggle_like error:", e)
            return {'success': False, 'message': str(e)}

    def add_comment(self, contest_id, ent_user_id, cmt_user_id, comment_text):
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pst_contest_cmt (CONTEST_ROUND, ENT_USER_ID, CMT_USER_ID, CMT)
                    VALUES (%s, %s, %s, %s)
                """, (contest_id, ent_user_id, cmt_user_id, comment_text))

                cur.execute("""
                    UPDATE pst_contest_round
                    SET CMT_CNT = CMT_CNT + 1, SCORE = SCORE + 10
                    WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                """, (contest_id, ent_user_id))
                conn.commit()
                conn.close()
                return {'success': True}
        except Exception as e:
            print("add_comment error:", e)
            return {'success': False, 'message': str(e)}

    def get_hall_of_fame(self, contest_id=None):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                if not contest_id:
                    cur.execute("SELECT CONTEST_ROUND FROM pst_contest_award ORDER BY CONTEST_ROUND DESC LIMIT 1")
                    r = cur.fetchone()
                    contest_id = r['CONTEST_ROUND'] if r else 1

                cur.execute("""
                    SELECT 
                        ca.CONTEST_ROUND,
                        ca.AWARD_PART,
                        ca.AWARD_CD,
                        a.AWARD_NM,
                        a.BADGE_IMG_PATH_FILE,
                        ca.SCORE,
                        ca.RANKING,
                        r.PET_NM,
                        k.KIND_NM,
                        k.KIND_CLASS,
                        r.TITLE,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                            ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                        END AS IMAGE_PATH,
                        u.USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        -- 호환용
                        ca.CONTEST_ROUND AS contest_id,
                        t.THEME_NM AS contest_title,
                        ca.AWARD_PART AS award_part,
                        ca.AWARD_CD AS award_cd,
                        a.AWARD_NM AS prize_name,
                        a.BADGE_IMG_PATH_FILE AS badge_img,
                        ca.SCORE AS score,
                        ca.RANKING AS ranking,
                        r.PET_NM AS pet_name,
                        k.KIND_NM AS pet_type,
                        r.TITLE AS title,
                        CASE 
                            WHEN r.PHT_PATH LIKE '/%%%%' THEN CONCAT(r.PHT_PATH, '/', r.PHT_FILE1)
                            ELSE CONCAT('/static/image/post/', r.PHT_FILE1)
                        END AS image_path,
                        u.USER_ID AS user_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile
                    FROM pst_contest_award ca
                    JOIN pst_contest c ON ca.CONTEST_ROUND = c.CONTEST_ROUND
                    JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                    JOIN pst_contest_round r ON ca.CONTEST_ROUND = r.CONTEST_ROUND AND ca.ENT_USER_ID = r.ENT_USER_ID
                    JOIN pst_user u ON SUBSTRING_INDEX(ca.ENT_USER_ID, '_post_', 1) = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    WHERE ca.CONTEST_ROUND = %s
                    ORDER BY ca.AWARD_PART ASC, ca.RANKING ASC
                """, (contest_id,))
                winners = cur.fetchall()
                conn.close()
                return winners
        except Exception as e:
            print("get_hall_of_fame error:", e)
            return []

service = PawStarService()
