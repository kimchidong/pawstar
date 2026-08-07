"""
Paw Star Contest Service (get_posts & get_post_detail query rewrite)
"""

from datetime import datetime, timedelta
import pymysql
import uuid
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

        st_dt = contest.get('ST_DT') or contest.get('start_date') or contest.get('ED_DT') or contest.get('end_date')
        if st_dt:
            if isinstance(st_dt, str):
                try:
                    st_dt_obj = datetime.strptime(st_dt[:10], "%Y-%m-%d")
                    contest['contest_year_month'] = f"{st_dt_obj.year}년 {st_dt_obj.month}월 콘테스트"
                except Exception:
                    contest['contest_year_month'] = "해당 년월 콘테스트"
            elif hasattr(st_dt, 'year'):
                contest['contest_year_month'] = f"{st_dt.year}년 {st_dt.month}월 콘테스트"
            else:
                contest['contest_year_month'] = "해당 년월 콘테스트"
        else:
            contest['contest_year_month'] = "해당 년월 콘테스트"

        stat = str(contest.get('CONTEST_STAT') or contest.get('contest_stat') or '').strip()
        stat_nm = str(contest.get('CONTEST_STAT_NM') or contest.get('status') or '').strip()
        
        now = datetime.now()
        end_dt = contest.get('ED_DT') or contest.get('end_date')

        # 상태코드가 종료(G001C002)이거나 상태명이 종료/마감인 경우
        if stat == 'G001C002' or stat_nm in ['종료', '마감', 'CLOSED', '종료됨', '콘테스트 마감']:
            contest['d_day_str'] = "종료"
            contest['is_closed'] = True
            return contest

        if not end_dt:
            contest['d_day_str'] = "상시 진행"
            contest['is_closed'] = False
            return contest

        if isinstance(end_dt, str):
            try:
                end_dt = datetime.strptime(end_dt[:10], "%Y-%m-%d")
            except Exception:
                contest['d_day_str'] = "상시 진행"
                contest['is_closed'] = False
                return contest

        # 종료일시가 현재 시점보다 지난 경우 자동 종료 처리
        if isinstance(end_dt, datetime) and end_dt < now:
            contest['d_day_str'] = "종료"
            contest['is_closed'] = True
            return contest

        diff_days = (end_dt.date() - now.date()).days
        if diff_days < 0:
            contest['d_day_str'] = "종료"
            contest['is_closed'] = True
        elif diff_days == 0:
            contest['d_day_str'] = "D-DAY Today"
            contest['is_closed'] = False
        else:
            contest['d_day_str'] = f"D-{diff_days}"
            contest['is_closed'] = False
        return contest

    def get_user_contest_entry_count(self, contest_id, base_user_id):
        conn = self.get_db_connection()
        if not conn:
            return 0
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                """, (contest_id, base_user_id))
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
        except Exception:
            return 1

    def format_pet_kind(self, kind_nm):
        if not kind_nm:
            return '🐾 반려동물'
        nm = str(kind_nm).strip()
        if any(c in nm for c in ['🐕', '🐈', '🐹', '🦜', '🐇', '🦔', '🦎', '🐠', '🦦', '🐾', '🐶', '🐱', '🐰']):
            return nm
        if '강아지' in nm or '개' in nm:
            icon = '🐕'
        elif '고양이' in nm:
            icon = '🐈'
        elif '햄스터' in nm:
            icon = '🐹'
        elif '앵무새' in nm or '새' in nm or '조류' in nm:
            icon = '🦜'
        elif '토끼' in nm:
            icon = '🐇'
        elif '고슴도치' in nm:
            icon = '🦔'
        elif '파충류' in nm or '도마뱀' in nm:
            icon = '🦎'
        elif '말' in nm or '큰동물' in nm:
            icon = '🐴'
        elif '돼지' in nm or '피그' in nm:
            icon = '🐷'
        elif '어류' in nm or '물고기' in nm or '관상어' in nm:
            icon = '🐠'
        elif '페럿' in nm:
            icon = '🦦'
        else:
            icon = '🐾'
        return f"{icon} {nm}"

    def get_pet_kinds(self):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT KIND_CD, KIND_NM, KIND_CLASS FROM pst_pet_kind ORDER BY KIND_CD ASC")
                rows = cur.fetchall()
                conn.close()
                for k in rows:
                    nm = k.get('KIND_NM', '')
                    k['DISPLAY_NM'] = self.format_pet_kind(nm)
                    k['ICON'] = k['DISPLAY_NM'].split()[0] if k['DISPLAY_NM'] else '🐾'
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
        if not user_id:
            return False
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pst_user WHERE USER_ID = %s", (user_id,))
                result = cur.fetchone()
                conn.close()
                return bool(result)
        except Exception as e:
            print("is_user_exists error:", e)
            return False

    def authenticate_user(self, user_id, password=None):
        """ 사용자 ID로 회원 정보 확인 및 로그인 인증 처리 """
        if not user_id:
            return False, "아이디를 입력해주세요."
        conn = self.get_db_connection()
        if not conn:
            return False, "DB 연결 실패"
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT USER_ID, NK_NM, PROFILE_URL FROM pst_user WHERE USER_ID = %s", (user_id,))
                user = cur.fetchone()
                conn.close()
                if user:
                    nk = user.get('NK_NM', user_id)
                    img = user.get('PROFILE_URL', '')
                    return True, {'user_id': user_id, 'nickname': nk, 'profile_img': img}
                return False, "존재하지 않는 회원입니다."
        except Exception as e:
            print("authenticate_user error:", e)
            return False, "로그인 처리 중 오류가 발생했습니다."

    def register_user(self, user_id, nickname, password="", profile_img="", **kwargs):
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            profile_url = profile_img or '/static/image/profile/default_profile.png'
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pst_user (USER_ID, NK_NM, PROFILE_URL, LGN_CNT, LGN_DT, JOIN_DT)
                    VALUES (%s, %s, %s, 1, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE 
                        NK_NM = VALUES(NK_NM),
                        PROFILE_URL = IF(VALUES(PROFILE_URL) != '' AND VALUES(PROFILE_URL) != '/static/image/profile/default_profile.png', VALUES(PROFILE_URL), PROFILE_URL),
                        LGN_CNT = LGN_CNT + 1, 
                        LGN_DT = NOW()
                """, (user_id, nickname, profile_url))
                conn.commit()

                cur.execute("SELECT USER_ID, NK_NM, PROFILE_URL FROM pst_user WHERE USER_ID = %s", (user_id,))
                user = cur.fetchone()
                conn.close()

                final_nk = user.get('NK_NM', nickname) if user else nickname
                final_img = user.get('PROFILE_URL', profile_url) if user else profile_url

                return {'USER_ID': user_id, 'NK_NM': final_nk, 'PROFILE_URL': final_img, 'user_id': user_id, 'nickname': final_nk, 'profile_img': final_img}
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
                    """, (user_id, nickname, profile_img))
                    conn.commit()
                    user_info = {
                        'USER_ID': user_id,
                        'NK_NM': nickname,
                        'PROFILE_URL': profile_img,
                        'user_id': user_id,
                        'nickname': nickname,
                        'profile_img': profile_img,
                        'is_new_user': True
                    }
                else:
                    # 로그인 성공 시 전달받은 최신 프로필 이미지가 유효하면 DB 및 반환 객체에 최신 프로필 이미지 항상 갱신 저장
                    if picture and picture.strip() and picture != '/static/image/profile/default_profile.png':
                        cur.execute("""
                            UPDATE pst_user 
                            SET PROFILE_URL = %s, LGN_CNT = LGN_CNT + 1, LGN_DT = NOW() 
                            WHERE USER_ID = %s
                        """, (picture.strip(), user_id))
                        latest_img = picture.strip()
                    else:
                        cur.execute("""
                            UPDATE pst_user 
                            SET LGN_CNT = LGN_CNT + 1, LGN_DT = NOW() 
                            WHERE USER_ID = %s
                        """, (user_id,))
                        latest_img = user.get('PROFILE_URL') or profile_img

                    conn.commit()
                    user_info = {
                        'USER_ID': user['USER_ID'],
                        'NK_NM': user.get('NK_NM', nickname),
                        'PROFILE_URL': latest_img,
                        'user_id': user['USER_ID'],
                        'nickname': user.get('NK_NM', nickname),
                        'profile_img': latest_img
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

    def update_user_profile(self, user_id, nickname, profile_img="", **kwargs):
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
                        WHERE USER_ID = %s
                    """, (nickname, profile_img, user_id))
                else:
                    cur.execute("""
                        UPDATE pst_user
                        SET NK_NM = %s
                        WHERE USER_ID = %s
                    """, (nickname, user_id))

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
                cur.execute("DELETE FROM pst_contest_round WHERE ENT_USER_ID = %s", (user_id,))
                cur.execute("DELETE FROM pst_user WHERE USER_ID = %s", (user_id,))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print("delete_user error:", e)
            return False

    def get_user_profile(self, user_id, contest_id='all'):
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

                user_info['user_id'] = user_info.get('USER_ID', user_id)
                user_info['nickname'] = user_info.get('NK_NM', user_id)
                user_info['profile_img'] = user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png')

                # 최초 가입일 및 최근 로그인 일시 포맷팅
                join_val = user_info.get('JOIN_DT') or user_info.get('join_dt') or user_info.get('JOIN_DATE') or user_info.get('created_at')
                if hasattr(join_val, 'strftime'):
                    user_info['join_date'] = join_val.strftime('%Y-%m-%d %H:%M:%S')
                elif join_val:
                    user_info['join_date'] = str(join_val)
                else:
                    user_info['join_date'] = '-'

                lgn_val = user_info.get('LGN_DT') or user_info.get('lgn_dt') or user_info.get('LAST_LOGIN') or user_info.get('last_login')
                if hasattr(lgn_val, 'strftime'):
                    user_info['last_login'] = lgn_val.strftime('%Y-%m-%d %H:%M:%S')
                elif lgn_val:
                    user_info['last_login'] = str(lgn_val)
                else:
                    user_info['last_login'] = '-'

                query = """
                    SELECT 
                        r.CONTEST_ROUND,
                        r.ROUND_NO,
                        r.ENT_USER_ID,
                        r.ENT_USER_ID AS USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        k.KIND_NM,
                        k.KIND_CLASS,
                        r.PET_NM,
                        r.TITLE,
                        r.CONTS,
                        r.PHT_FILE_PATH1,
                        r.PHT_FILE_PATH2,
                        r.PHT_FILE_PATH1 AS IMAGE_PATH,
                        r.VW_CNT,
                        r.LIKE_CNT,
                        r.CMT_CNT,
                        COALESCE(r.SHARE_CNT, 0) AS SHARE_CNT,
                        r.SHARE_SN,
                        r.SCORE,
                        r.ENT_DT,
                        -- 호환 키
                        r.CONTEST_ROUND AS contest_id,
                        r.ROUND_NO AS round_no,
                        r.ENT_USER_ID AS user_id,
                        CONCAT(r.CONTEST_ROUND, '_', r.ENT_USER_ID) AS post_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        k.KIND_NM AS pet_type,
                        r.PET_NM AS pet_name,
                        r.TITLE AS title,
                        r.CONTS AS content,
                        r.PHT_FILE_PATH1 AS image_path,
                        r.VW_CNT AS view_count,
                        r.LIKE_CNT AS like_count,
                        r.CMT_CNT AS comment_count,
                        COALESCE(r.SHARE_CNT, 0) AS share_count,
                        r.SHARE_SN AS share_sn,
                        r.SCORE AS score
                    FROM pst_contest_round r
                    JOIN pst_user u ON r.ENT_USER_ID = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    WHERE r.ENT_USER_ID = %s
                """
                params = [user_id]
                if contest_id and str(contest_id) != 'all':
                    query += " AND r.CONTEST_ROUND = %s"
                    params.append(contest_id)

                query += " ORDER BY r.ENT_DT DESC"
                cur.execute(query, tuple(params))
                my_posts = cur.fetchall()

                for p in my_posts:
                    dt_val = p.get('ENT_DT')
                    if hasattr(dt_val, 'strftime'):
                        dt_str = dt_val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dt_str = str(dt_val or '')
                    p['ENT_DT'] = dt_str
                    p['created_at'] = dt_str
                    k_fmt = self.format_pet_kind(p.get('KIND_NM') or p.get('pet_type'))
                    p['KIND_NM'] = k_fmt
                    p['pet_type'] = k_fmt

                my_post_count = len(my_posts)
                total_score = sum(p.get('SCORE', 0) for p in my_posts)
                total_likes = sum(p.get('LIKE_CNT', 0) for p in my_posts)

                award_query = """
                    SELECT 
                        ca.CONTEST_ROUND, ca.AWARD_CD, ca.AWARD_PART, ca.RANKING, ca.KIND_CD,
                        a.AWARD_NM, a.BADGE_IMG_PATH_FILE,
                        ca.CONTEST_ROUND AS contest_id, a.AWARD_NM AS prize_name, a.BADGE_IMG_PATH_FILE AS badge_img,
                        r.TITLE AS post_title, r.TITLE AS title, r.PHT_FILE_PATH1 AS image_path, t.THEME_NM AS theme_title,
                        r.ROUND_NO, r.ENT_USER_ID, r.ENT_USER_ID AS user_id, r.CONTS AS content, r.CONTS, r.SCORE,
                        r.VW_CNT AS view_count, r.LIKE_CNT AS like_count, r.CMT_CNT AS comment_count,
                        r.VW_CNT, r.LIKE_CNT, r.CMT_CNT,
                        r.PET_NM AS pet_name, r.PET_NM,
                        k.KIND_NM AS pet_type, k.KIND_NM,
                        u.NK_NM AS user_nickname, u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        CONCAT(ca.CONTEST_ROUND, '_', r.ENT_USER_ID) AS post_id
                    FROM pst_contest_award ca
                    JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                    LEFT JOIN pst_contest_round r ON ca.CONTEST_ROUND = r.CONTEST_ROUND AND ca.ROUND_NO = r.ROUND_NO
                    LEFT JOIN pst_user u ON r.ENT_USER_ID = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    LEFT JOIN pst_contest c ON ca.CONTEST_ROUND = c.CONTEST_ROUND
                    LEFT JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    WHERE ca.ENT_USER_ID = %s
                """
                award_params = [user_id]
                award_query += " ORDER BY ca.CONTEST_ROUND DESC, ca.RANKING ASC"
                cur.execute(award_query, tuple(award_params))
                raw_awards = cur.fetchall()

                # 동일 회차 및 출전작 단위 그룹핑 (한 로우에 복수 수상 뱃지 세트 구성)
                grouped_awards = {}
                for a in raw_awards:
                    key = (a['CONTEST_ROUND'], a.get('ROUND_NO'), a.get('post_title'))
                    k_fmt = self.format_pet_kind(a.get('KIND_NM') or a.get('pet_type'))
                    if key not in grouped_awards:
                        grouped_awards[key] = {
                            'CONTEST_ROUND': a['CONTEST_ROUND'],
                            'contest_id': a['CONTEST_ROUND'],
                            'ROUND_NO': a.get('ROUND_NO'),
                            'post_id': a.get('post_id'),
                            'post_title': a.get('post_title'),
                            'title': a.get('title') or a.get('post_title'),
                            'image_path': a.get('image_path'),
                            'theme_title': a.get('theme_title'),
                            'ENT_USER_ID': a.get('ENT_USER_ID'),
                            'user_id': a.get('user_id') or a.get('ENT_USER_ID'),
                            'user_nickname': a.get('user_nickname') or user_info.get('NK_NM', user_id),
                            'NK_NM': a.get('NK_NM') or user_info.get('NK_NM', user_id),
                            'user_profile': a.get('user_profile') or user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png'),
                            'PROFILE_URL': a.get('PROFILE_URL') or user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png'),
                            'pet_name': a.get('pet_name') or '반려동물',
                            'PET_NM': a.get('PET_NM') or '반려동물',
                            'pet_type': k_fmt,
                            'KIND_NM': k_fmt,
                            'content': a.get('content') or a.get('CONTS') or '',
                            'CONTS': a.get('CONTS') or '',
                            'SCORE': a.get('SCORE') or 0,
                            'score': a.get('SCORE') or 0,
                            'view_count': a.get('view_count') or 0,
                            'VW_CNT': a.get('VW_CNT') or 0,
                            'like_count': a.get('like_count') or 0,
                            'LIKE_CNT': a.get('LIKE_CNT') or 0,
                            'comment_count': a.get('comment_count') or 0,
                            'CMT_CNT': a.get('CMT_CNT') or 0,
                            'awards': []
                        }
                    
                    b_img = a.get('badge_img') or a.get('BADGE_IMG_PATH_FILE') or ''
                    if not b_img and a.get('AWARD_CD'):
                        b_img = f"/static/image/badge/{a.get('AWARD_CD')}.png"
                    
                    award_item = {
                        'AWARD_CD': a.get('AWARD_CD'),
                        'AWARD_PART': a.get('AWARD_PART'),
                        'AWARD_NM': a.get('AWARD_NM') or a.get('prize_name'),
                        'RANKING': a.get('RANKING'),
                        'KIND_CD': a.get('KIND_CD') or a.get('round_kind_cd'),
                        'prize_name': a.get('prize_name'),
                        'badge_img': b_img,
                        'BADGE_IMG_PATH_FILE': b_img
                    }
                    grouped_awards[key]['awards'].append(award_item)

                my_awards = list(grouped_awards.values())
                # 가장 최근 회차 순으로 정렬 (CONTEST_ROUND 내림차순)
                my_awards.sort(key=lambda x: int(x.get('CONTEST_ROUND') or 0), reverse=True)

                conn.close()
                return {
                    'user_info': {
                        'USER_ID': user_info['USER_ID'],
                        'NK_NM': user_info.get('NK_NM', user_id),
                        'PROFILE_URL': user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png'),
                        'user_id': user_info['USER_ID'],
                        'nickname': user_info.get('NK_NM', user_id),
                        'profile_img': user_info.get('PROFILE_URL', '/static/image/profile/default_profile.png'),
                        'join_date': user_info.get('join_date', '-'),
                        'last_login': user_info.get('last_login', '-'),
                        'JOIN_DT': str(user_info.get('JOIN_DT', '')),
                        'LGN_DT': str(user_info.get('LGN_DT', '')),
                        'LGN_CNT': user_info.get('LGN_CNT', 0)
                    },
                    'stats': {
                        'my_post_count': my_post_count,
                        'total_score': total_score,
                        'total_likes': total_likes,
                        'award_count': len(raw_awards)
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

    def create_contest_entry(self, contest_id, user_id, kind_cd, pet_name, title, content, file_path1, file_path2=""):
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        
        entry_cnt = self.get_user_contest_entry_count(contest_id, user_id)
        if entry_cnt >= 5:
            return {
                'success': False,
                'message': f'해당 회차에는 회원 1인당 최대 5회까지만 출전이 가능합니다. (현재 {entry_cnt}/5회 출전 완료)'
            }

        actual_ent_user_id = user_id

        if not self.is_user_exists(user_id):
            self.register_user(user_id, user_id)

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
                    SELECT COALESCE(MAX(ROUND_NO), 0) + 1 AS next_round_no 
                    FROM pst_contest_round 
                    WHERE CONTEST_ROUND = %s
                """, (contest_id,))
                row_r = cur.fetchone()
                next_round_no = row_r['next_round_no'] if row_r else 1

                share_sn = f"S-{uuid.uuid4()}"
                cur.execute("""
                    INSERT INTO pst_contest_round 
                    (CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, PET_NM, TITLE, CONTS, PHT_FILE_PATH1, PHT_FILE_PATH2, SHARE_SN, SHARE_CNT)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, (contest_id, next_round_no, actual_ent_user_id, kind_cd, pet_name, title, content, file_path1, file_path2, share_sn))
                conn.commit()
                conn.close()
                return {'success': True, 'ent_user_id': actual_ent_user_id, 'round_no': next_round_no, 'share_sn': share_sn}
        except Exception as e:
            print("create_contest_entry error:", e)
            return {'success': False, 'message': str(e)}

    def get_or_create_share_sn(self, contest_id, round_no):
        """ 게시물의 공유 고유 번호(SHARE_SN: 'S-' 접두어 포함) 반환 (없을 경우 자동 생성 후 DB 저장) """
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT SHARE_SN FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (contest_id, round_no))
                row = cur.fetchone()
                if row and row.get('SHARE_SN'):
                    sn = row['SHARE_SN']
                    if not sn.startswith('S-'):
                        sn = f"S-{sn}"
                        cur.execute("""
                            UPDATE pst_contest_round
                            SET SHARE_SN = %s
                            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                        """, (sn, contest_id, round_no))
                        conn.commit()
                    conn.close()
                    return sn

                new_sn = f"S-{uuid.uuid4()}"
                cur.execute("""
                    UPDATE pst_contest_round
                    SET SHARE_SN = %s
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (new_sn, contest_id, round_no))
                conn.commit()
                conn.close()
                return new_sn
        except Exception as e:
            print("get_or_create_share_sn error:", e)
            if conn:
                conn.close()
            return None

    def increment_share_count_on_signup(self, contest_id, round_no, share_sn, user_id=None):
        """ 공유주소(CONTEST_ROUND, ROUND_NO, SHARE_SN)를 통한 회원가입 및 기존 회원 로그인 유입 시 PST_CONTEST_SHARE 저장, 공유횟수 +1 및 점수 +1 반영
            단, 진행 중인 회차(CONTEST_STAT = 'G001C001')에 한해서만 반영. 과거(종료) 회차 및 중복 유입/자가 공유는 무시. """
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                # 1. 해당 회차가 현재 진행 중인지 확인 (종료된 과거 회차는 반영 불가)
                cur.execute("""
                    SELECT c.CONTEST_STAT
                    FROM pst_contest c
                    WHERE c.CONTEST_ROUND = %s
                """, (contest_id,))
                contest_row = cur.fetchone()
                if not contest_row:
                    print(f"increment_share_count_on_signup: contest {contest_id} not found, skip.")
                    conn.close()
                    return False

                contest_stat = str(contest_row.get('CONTEST_STAT') or '').strip()
                if contest_stat != 'G001C001':
                    # 종료된 과거 회차 → 공유 카운트/점수 반영 차단
                    print(f"increment_share_count_on_signup: contest {contest_id} is not active (STAT={contest_stat}), skip share score.")
                    conn.close()
                    return False

                # 2. 게시물(SHARE_SN) 및 작성자 정보 확인
                cur.execute("""
                    SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, COALESCE(SHARE_CNT, 0) AS SHARE_CNT
                    FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_SN = %s
                """, (contest_id, round_no, share_sn))
                row = cur.fetchone()
                if not row:
                    conn.close()
                    return False

                # 게시글 작성자 본인 유입 시 점수 반영 불가
                author_id = row.get('ENT_USER_ID')
                if user_id and author_id and str(user_id) == str(author_id):
                    print(f"increment_share_count_on_signup: user {user_id} is author of contest {contest_id}-{round_no}, skip self-share.")
                    conn.close()
                    return False

                # 3. 공유 유입 이력 기록 (중복 유입 방지)
                if user_id:
                    affected = cur.execute("""
                        INSERT IGNORE INTO pst_contest_share (CONTEST_ROUND, ROUND_NO, SHARE_USER_ID)
                        VALUES (%s, %s, %s)
                    """, (contest_id, round_no, user_id))
                    if affected == 0:
                        # 이미 해당 유저의 공유 유입 점수가 반영되었음
                        print(f"increment_share_count_on_signup: user {user_id} already registered share for {contest_id}-{round_no}, skip duplicate.")
                        conn.close()
                        return False

                # 4. 공유 카운트 및 점수 반영
                new_share_cnt = row['SHARE_CNT'] + 1
                self.sync_and_get_post_stats(cur, contest_id, round_no, share_cnt_override=new_share_cnt)
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print("increment_share_count_on_signup error:", e)
            if conn:
                conn.close()
            return False

    def create_post(self, contest_id, user_id, pet_name, pet_type, title, content, media_url="", file_path1="", file_path2="", **kwargs):
        path1 = file_path1 or media_url or "/static/image/paw/default_pet.jpg"
        path2 = file_path2 or path1

        res = self.create_contest_entry(contest_id, user_id, pet_type, pet_name, title, content, path1, path2)
        if not res.get('success'):
            return res

        actual_user_id = res.get('ent_user_id', user_id)
        round_no = res.get('round_no', 1)
        return {
            'success': True,
            'CONTEST_ROUND': contest_id,
            'ROUND_NO': round_no,
            'ENT_USER_ID': actual_user_id,
            'post_id': f"{contest_id}_{round_no}",
            'PET_NM': pet_name,
            'TITLE': title
        }

    def delete_contest_entry(self, post_id, user_id):
        """ 콘테스트 출전물 삭제 (출전 포기) """
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}

        try:
            contest_round = None
            round_no = None
            ent_user_id = None

            post_id_str = str(post_id)
            if '_' in post_id_str:
                parts = post_id_str.split('_', 1)
                contest_round = parts[0]
                if parts[1].isdigit():
                    round_no = int(parts[1])
                else:
                    ent_user_id = parts[1]
            else:
                ent_user_id = post_id_str

            with conn.cursor() as cur:
                # 1. 해당 출전물 정보 조회
                if contest_round and round_no:
                    cur.execute("""
                        SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID 
                        FROM pst_contest_round 
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                    """, (contest_round, round_no))
                elif contest_round and ent_user_id:
                    cur.execute("""
                        SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID 
                        FROM pst_contest_round 
                        WHERE CONTEST_ROUND = %s AND ENT_USER_ID = %s
                    """, (contest_round, ent_user_id))
                else:
                    cur.execute("""
                        SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID 
                        FROM pst_contest_round 
                        WHERE ENT_USER_ID = %s
                    """, (ent_user_id,))
                
                entry = cur.fetchone()
                if not entry:
                    conn.close()
                    return {'success': False, 'message': '존재하지 않거나 이미 삭제된 출전물입니다.'}

                c_round = entry['CONTEST_ROUND']
                r_no = entry['ROUND_NO']
                owner_id = entry['ENT_USER_ID']

                # 2. 본인 소유 확인 (단, 관리자인 경우 허용)
                if owner_id != user_id and user_id != 'admin':
                    conn.close()
                    return {'success': False, 'message': '본인의 출전물만 포기(삭제)할 수 있습니다.'}

                # 3. 회차 마감 여부 검증 (종료된 회차는 삭제 불가)
                cur.execute("""
                    SELECT CONTEST_STAT FROM pst_contest WHERE CONTEST_ROUND = %s
                """, (c_round,))
                c_info = cur.fetchone()
                if c_info and c_info.get('CONTEST_STAT') == 'G001C002':
                    conn.close()
                    return {'success': False, 'message': '이미 마감(종료)된 회차의 출전물은 포기(삭제)할 수 없습니다.'}

                # 4. 관련 하위 레코드 및 출전물 삭제
                cur.execute("DELETE FROM pst_contest_like WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                cur.execute("DELETE FROM pst_contest_cmt WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                cur.execute("DELETE FROM pst_contest_vw WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))
                cur.execute("DELETE FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (c_round, r_no))

                conn.commit()
                conn.close()
                return {'success': True, 'message': '출전이 성공적으로 포기(삭제)되었습니다.', 'post_id': post_id_str, 'contest_round': c_round, 'round_no': r_no}
        except Exception as e:
            print("delete_contest_entry error:", e)
            if conn:
                conn.close()
            return {'success': False, 'message': str(e)}

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
                    r.ROUND_NO,
                    r.ENT_USER_ID,
                    r.ENT_USER_ID AS USER_ID,
                    u.NK_NM,
                    COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                    k.KIND_NM,
                    k.KIND_CLASS,
                    r.PET_NM,
                    r.TITLE,
                    r.CONTS,
                    r.PHT_FILE_PATH1,
                    r.PHT_FILE_PATH2,
                    r.PHT_FILE_PATH1 AS IMAGE_PATH,
                    r.VW_CNT,
                    r.LIKE_CNT,
                    r.CMT_CNT,
                    r.SCORE,
                    r.ENT_DT AS ENT_DT,
                    r.TOTAL_RANKING,
                    r.KIND_RANKING,
                    -- 호환용
                    c.CONTEST_STAT AS contest_stat,
                    r.CONTEST_ROUND AS contest_id,
                    r.ROUND_NO AS round_no,
                    r.ENT_USER_ID AS user_id,
                    CONCAT(r.CONTEST_ROUND, '_', r.ROUND_NO) AS post_id,
                    u.NK_NM AS user_nickname,
                    COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                    k.KIND_NM AS pet_type,
                    r.PET_NM AS pet_name,
                    r.TITLE AS title,
                    r.CONTS AS content,
                    r.PHT_FILE_PATH1 AS file_path,
                    r.PHT_FILE_PATH1 AS list_file_name,
                    r.PHT_FILE_PATH1 AS image_path,
                    COALESCE(NULLIF(r.PHT_FILE_PATH2, ''), r.PHT_FILE_PATH1) AS popup_image_path,
                    (SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) AS view_count,
                    (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) AS like_count,
                    (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) AS comment_count,
                    COALESCE(r.SHARE_CNT, 0) AS share_count,
                    r.SHARE_SN AS share_sn,
                    ((SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) * 1 +
                     (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) * 5 +
                     (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) * 10 +
                     COALESCE(r.SHARE_CNT, 0) * 10) AS score,
                    r.ENT_DT AS created_at
                FROM pst_contest_round r
                LEFT JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                JOIN pst_user u ON r.ENT_USER_ID = u.USER_ID
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

            if sort_type == 'popular' or sort_type == 'score' or sort_type == 'high_score':
                query += " ORDER BY r.SCORE DESC, r.CMT_CNT DESC, r.LIKE_CNT DESC, r.VW_CNT DESC, r.ENT_DT DESC"
            elif sort_type == 'low_score':
                query += " ORDER BY r.SCORE ASC, r.ENT_DT ASC"
            else:
                query += " ORDER BY r.ENT_DT DESC"

            with conn.cursor() as cur:
                cur.execute(query, params)
                all_rows = cur.fetchall()

                liked_round_nos = set()
                commented_round_nos = set()
                viewed_round_nos = set()
                shared_round_nos = set()
                if current_user_id:
                    cur.execute("""
                        SELECT ROUND_NO FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND LIKE_USER_ID = %s
                    """, (contest_id, current_user_id))
                    liked_rows = cur.fetchall()
                    liked_round_nos = {r['ROUND_NO'] for r in liked_rows}

                    cur.execute("""
                        SELECT DISTINCT ROUND_NO FROM pst_contest_cmt
                        WHERE CONTEST_ROUND = %s AND CMT_USER_ID = %s
                    """, (contest_id, current_user_id))
                    commented_rows = cur.fetchall()
                    commented_round_nos = {r['ROUND_NO'] for r in commented_rows}

                    cur.execute("""
                        SELECT DISTINCT ROUND_NO FROM pst_contest_vw
                        WHERE CONTEST_ROUND = %s AND VW_USER_ID = %s
                    """, (contest_id, current_user_id))
                    viewed_rows = cur.fetchall()
                    viewed_round_nos = {r['ROUND_NO'] for r in viewed_rows}

                    cur.execute("""
                        SELECT DISTINCT ROUND_NO FROM pst_contest_share
                        WHERE CONTEST_ROUND = %s AND SHARE_USER_ID = %s
                    """, (contest_id, current_user_id))
                    shared_rows = cur.fetchall()
                    shared_round_nos = {r['ROUND_NO'] for r in shared_rows}

                # 3. 해당 회차의 모든 수상 기록 조회 (전체부문 G002P001 -> 품종부문 G002P002 순서 정렬)
                cur.execute("""
                    SELECT 
                        ca.CONTEST_ROUND,
                        ca.ROUND_NO,
                        ca.AWARD_PART,
                        ca.AWARD_CD,
                        COALESCE(a.AWARD_NM, '당선작') AS AWARD_NM,
                        a.BADGE_IMG_PATH_FILE,
                        ca.RANKING
                    FROM pst_contest_award ca
                    LEFT JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                    WHERE ca.CONTEST_ROUND = %s
                    ORDER BY ca.AWARD_PART ASC, ca.RANKING ASC
                """, (contest_id,))
                award_rows = cur.fetchall()

                awards_map = {}
                for a_row in award_rows:
                    r_no = a_row['ROUND_NO']
                    if r_no not in awards_map:
                        awards_map[r_no] = []
                    
                    b_file = a_row.get('BADGE_IMG_PATH_FILE') or a_row.get('AWARD_CD') or ''
                    if b_file and not b_file.startswith('/') and not b_file.startswith('http'):
                        b_fn = b_file.split('/')[-1]
                        if not b_fn.lower().endswith(('.png', '.jpg', '.svg', '.jpeg')):
                            b_fn += '.png'
                        b_url = f'/static/image/badge/{b_fn}'
                    else:
                        b_url = b_file or '/static/image/badge/P001A101.png'
                    
                    b_url = b_url.replace('.webp', '.png')

                    awards_map[r_no].append({
                        'award_part': a_row['AWARD_PART'],
                        'award_part_nm': '전체부문' if a_row['AWARD_PART'] == 'G002P001' else '품종부문',
                        'award_cd': a_row['AWARD_CD'],
                        'award_nm': a_row['AWARD_NM'],
                        'badge_img': b_url,
                        'ranking': a_row['RANKING']
                    })

                total_count = len(all_rows)
                total_pages = max(1, (total_count + per_page - 1) // per_page)
                page = max(1, min(page, total_pages))
                start_idx = (page - 1) * per_page
                paged_rows = all_rows[start_idx:start_idx + per_page]

                # 월배치 순위 산출 규칙과 100% 동일한 정렬 & 동률 처리
                # (우선순위: SCORE DESC -> CMT_CNT DESC -> LIKE_CNT DESC -> VW_CNT DESC)
                sorted_all = sorted(all_rows, key=lambda x: (
                    x.get('SCORE', 0),
                    x.get('CMT_CNT', 0),
                    x.get('LIKE_CNT', 0),
                    x.get('VW_CNT', 0)
                ), reverse=True)

                current_rank = 1
                prev_key = None
                rank_info_map = {}
                rank_counts = {}

                for item in sorted_all:
                    key = (item.get('SCORE', 0), item.get('CMT_CNT', 0), item.get('LIKE_CNT', 0), item.get('VW_CNT', 0))
                    if prev_key is not None and key != prev_key:
                        current_rank += 1
                    
                    prev_key = key
                    r_no = item['ROUND_NO']
                    rank_info_map[r_no] = current_rank
                    rank_counts[current_rank] = rank_counts.get(current_rank, 0) + 1

                posts = []
                for row in paged_rows:
                    dt_val = row.get('ENT_DT')
                    if hasattr(dt_val, 'strftime'):
                        dt_str = dt_val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dt_str = str(dt_val or '')
                    row['ENT_DT'] = dt_str
                    row['created_at'] = dt_str
                    
                    r_val = rank_info_map.get(row['ROUND_NO'], None)
                    if r_val and r_val <= 3:
                        row['rank_candidate'] = r_val
                        row['is_co_rank'] = (rank_counts.get(r_val, 1) > 1)
                    else:
                        row['rank_candidate'] = None
                        row['is_co_rank'] = False

                    k_formatted = self.format_pet_kind(row.get('KIND_NM') or row.get('pet_type'))
                    row['KIND_NM'] = k_formatted
                    row['pet_type'] = k_formatted

                    is_closed_stat = self.is_contest_closed(contest_id)
                    row['is_closed'] = is_closed_stat
                    row['closed'] = is_closed_stat
                    if is_closed_stat:
                        row['CONTEST_STAT'] = 'G001C002'
                        row['STATUS_CD'] = 'G001C002'

                    row['awards'] = awards_map.get(row['ROUND_NO'], [])
                    row['actions'] = {
                        'is_liked': row['ROUND_NO'] in liked_round_nos,
                        'is_commented': row['ROUND_NO'] in commented_round_nos,
                        'is_viewed': row['ROUND_NO'] in viewed_round_nos,
                        'is_shared': row['ROUND_NO'] in shared_round_nos
                    }
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

    def get_post_detail(self, contest_id, target_id, current_user_id=None, share_sn=None):
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        r.CONTEST_ROUND,
                        r.ROUND_NO,
                        r.ENT_USER_ID,
                        r.ENT_USER_ID AS USER_ID,
                        u.NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        k.KIND_NM,
                        k.KIND_CLASS,
                        r.PET_NM,
                        r.TITLE,
                        r.CONTS,
                        r.PHT_FILE_PATH1,
                        r.PHT_FILE_PATH2,
                        r.PHT_FILE_PATH1 AS IMAGE_PATH,
                        r.VW_CNT,
                        r.LIKE_CNT,
                        r.CMT_CNT,
                        r.SCORE,
                        r.ENT_DT AS ENT_DT,
                        -- 콘테스트명
                        COALESCE(t.THEME_NM, CONCAT('제', r.CONTEST_ROUND, '회 콘테스트')) AS contest_title,
                        -- 호환용
                        r.CONTEST_ROUND AS contest_id,
                        r.ROUND_NO AS round_no,
                        r.ENT_USER_ID AS user_id,
                        CONCAT(r.CONTEST_ROUND, '_', r.ROUND_NO) AS post_id,
                        u.NK_NM AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile,
                        k.KIND_NM AS pet_type,
                        r.PET_NM AS pet_name,
                        r.TITLE AS title,
                        r.CONTS AS content,
                        r.PHT_FILE_PATH1 AS file_path,
                        r.PHT_FILE_PATH1 AS list_file_name,
                        r.PHT_FILE_PATH1 AS image_path,
                        COALESCE(NULLIF(r.PHT_FILE_PATH2, ''), r.PHT_FILE_PATH1) AS popup_image_path,
                        (SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) AS view_count,
                        (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) AS like_count,
                        (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) AS comment_count,
                        COALESCE(r.SHARE_CNT, 0) AS share_count,
                        r.SHARE_SN AS share_sn,
                        ((SELECT COUNT(*) FROM pst_contest_vw v WHERE v.CONTEST_ROUND = r.CONTEST_ROUND AND v.ROUND_NO = r.ROUND_NO) * 1 +
                         (SELECT COUNT(*) FROM pst_contest_like l WHERE l.CONTEST_ROUND = r.CONTEST_ROUND AND l.ROUND_NO = r.ROUND_NO) * 5 +
                         (SELECT COUNT(*) FROM pst_contest_cmt c WHERE c.CONTEST_ROUND = r.CONTEST_ROUND AND c.ROUND_NO = r.ROUND_NO) * 10 +
                         COALESCE(r.SHARE_CNT, 0) * 10) AS score,
                        r.ENT_DT AS created_at
                    FROM pst_contest_round r
                    JOIN pst_user u ON r.ENT_USER_ID = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON r.KIND_CD = k.KIND_CD
                    LEFT JOIN pst_contest c ON r.CONTEST_ROUND = c.CONTEST_ROUND
                    LEFT JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    WHERE r.CONTEST_ROUND = %s AND (r.ROUND_NO = %s OR r.ENT_USER_ID = %s)
                    ORDER BY r.ENT_DT DESC
                    LIMIT 1
                """, (contest_id, target_id, target_id))
                post = cur.fetchone()
                if not post:
                    conn.close()
                    return None

                # contest_round, round_no, share_sn 3개 값 엄격 100% 일치 검증
                if share_sn is not None and str(share_sn).strip() != '':
                    db_sn = str(post.get('SHARE_SN') or post.get('share_sn') or '').strip()
                    target_sn = str(share_sn).strip()
                    if db_sn != target_sn:
                        conn.close()
                        return None

                is_closed_stat = self.is_contest_closed(contest_id)
                post['is_closed'] = is_closed_stat
                post['closed'] = is_closed_stat
                if is_closed_stat:
                    post['CONTEST_STAT'] = 'G001C002'
                    post['STATUS_CD'] = 'G001C002'

                round_no = post['ROUND_NO']

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
                    JOIN pst_user u ON c.CMT_USER_ID = u.USER_ID
                    WHERE c.CONTEST_ROUND = %s AND c.ROUND_NO = %s
                    ORDER BY c.CMD_DT ASC
                """, (contest_id, round_no))
                comments = cur.fetchall()
                if comments:
                    for c in comments:
                        c_uid = str(c.get('USER_ID') or c.get('user_id') or '')
                        c['is_mine'] = bool(current_user_id and c_uid == str(current_user_id))

                is_liked = False
                is_commented = False
                is_viewed = False
                is_shared = False
                if current_user_id:
                    cur.execute("""
                        SELECT 1 FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND LIKE_USER_ID = %s
                    """, (contest_id, round_no, current_user_id))
                    is_liked = bool(cur.fetchone())

                    cur.execute("""
                        SELECT 1 FROM pst_contest_cmt
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND CMT_USER_ID = %s
                    """, (contest_id, round_no, current_user_id))
                    is_commented = bool(cur.fetchone())

                    cur.execute("""
                        SELECT 1 FROM pst_contest_vw
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND VW_USER_ID = %s
                    """, (contest_id, round_no, current_user_id))
                    is_viewed = bool(cur.fetchone())

                    cur.execute("""
                        SELECT 1 FROM pst_contest_share
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND SHARE_USER_ID = %s
                    """, (contest_id, round_no, current_user_id))
                    is_shared = bool(cur.fetchone())

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
                post['actions'] = {'is_liked': is_liked, 'is_commented': is_commented, 'is_viewed': is_viewed, 'is_shared': is_shared}
                conn.close()
                return post
        except Exception as e:
            print("get_post_detail error:", e)
            return None

    def sync_and_get_post_stats(self, cur, contest_id, round_no, share_cnt_override=None):
        """
        4가지 평가 요소(조회/좋아요/댓글/공유) 이벤트 발생 시 공통 적용:
        1. 하위 테이블 및 pst_contest_round에서 실제 4요소 개수 DB 재조회
        2. 조회된 개수로 총 점수(SCORE) 계산 (VW: 1, LIKE: 5, CMT: 10, SHARE: 10)
        3. DB pst_contest_round 테이블에 4요소 카운트 및 SCORE 반영 UPDATE
        4. DB에서 최종 4요소 및 SCORE를 반환
        """
        # 1. DB에서 하위 테이블 개수 재조회
        cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_vw WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (contest_id, round_no))
        vw_tbl_cnt = cur.fetchone()['cnt']

        cur.execute("SELECT COALESCE(VW_CNT, 0) AS r_vw, COALESCE(SHARE_CNT, 0) AS r_share FROM pst_contest_round WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (contest_id, round_no))
        r_row = cur.fetchone()
        r_vw = r_row['r_vw'] if r_row else 0
        
        # 조회수: 테이블 레코드 수와 round 누적값 중 더 큰 값을 적용 (최소 누적 수치 보장)
        vw_cnt = max(vw_tbl_cnt, r_vw)

        cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_like WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (contest_id, round_no))
        like_cnt = cur.fetchone()['cnt']

        cur.execute("SELECT COUNT(*) AS cnt FROM pst_contest_cmt WHERE CONTEST_ROUND = %s AND ROUND_NO = %s", (contest_id, round_no))
        cmt_cnt = cur.fetchone()['cnt']

        if share_cnt_override is not None:
            share_cnt = share_cnt_override
        else:
            share_cnt = r_row['r_share'] if r_row else 0

        # 2. 총 점수 계산 (조회 1점, 좋아요 5점, 댓글 10점, 공유 10점)
        calc_score = (vw_cnt * 1) + (like_cnt * 5) + (cmt_cnt * 10) + (share_cnt * 10)

        # 3. DB pst_contest_round 최신화 UPDATE
        cur.execute("""
            UPDATE pst_contest_round
            SET VW_CNT = %s, LIKE_CNT = %s, CMT_CNT = %s, SHARE_CNT = %s, SCORE = %s
            WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
        """, (vw_cnt, like_cnt, cmt_cnt, share_cnt, calc_score, contest_id, round_no))

        return {
            'view_count': vw_cnt,
            'like_count': like_cnt,
            'comment_count': cmt_cnt,
            'share_count': share_cnt,
            'score': calc_score,
            'new_score': calc_score
        }

    def is_contest_closed(self, contest_id):
        """ 백엔드 서버사이드 검증: 특정 회차가 마감/종료(G001C002) 상태인지 확인 """
        conn = self.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT CONTEST_STAT
                    FROM pst_contest
                    WHERE CONTEST_ROUND = %s
                    LIMIT 1
                """, (contest_id,))
                r = cur.fetchone()
                conn.close()
                if r:
                    stat = str(r.get('CONTEST_STAT') or '')
                    if stat in ['G001C002', 'CLOSED', '마감', '종료']:
                        return True
                return False
        except Exception as e:
            print("is_contest_closed check error:", e)
            if conn: conn.close()
            return False

    def increase_view_count(self, contest_id, target_id, view_user_id=None, client_ip=None):
        if self.is_contest_closed(contest_id):
            return {'view_count': 0, 'like_count': 0, 'comment_count': 0, 'new_score': 0, 'already_viewed': True, 'is_ended': True}

        conn = self.get_db_connection()
        if not conn:
            return {'view_count': 0, 'like_count': 0, 'comment_count': 0, 'new_score': 0, 'already_viewed': False}

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ROUND_NO FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND (ROUND_NO = %s OR ENT_USER_ID = %s)
                    ORDER BY ENT_DT DESC LIMIT 1
                """, (contest_id, target_id, target_id))
                r_info = cur.fetchone()
                if not r_info:
                    conn.close()
                    return {'view_count': 0, 'like_count': 0, 'comment_count': 0, 'new_score': 0, 'already_viewed': False}
                round_no = r_info['ROUND_NO']

                # 1. DB pst_contest_round 의 누적 조회수(VW_CNT) 1 무조건 가산
                cur.execute("""
                    UPDATE pst_contest_round
                    SET VW_CNT = COALESCE(VW_CNT, 0) + 1
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                """, (contest_id, round_no))

                vw_user = view_user_id
                if not vw_user:
                    ip_str = str(client_ip or 'GUEST').replace(':', '_').replace('.', '_')
                    vw_user = f"ANON_{ip_str}"

                # 2. 조회 이력 테이블(pst_contest_vw)에도 저장
                cur.execute("""
                    INSERT INTO pst_contest_vw (CONTEST_ROUND, ROUND_NO, VW_USER_ID, VW_DT)
                    VALUES (%s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE VW_DT = NOW()
                """, (contest_id, round_no, vw_user))

                # 3. DB에서 4요소 재조회 -> 점수 계산 -> DB 업데이트 -> 최종 DB 조회
                stats = self.sync_and_get_post_stats(cur, contest_id, round_no)
                conn.commit()
                conn.close()

                return {
                    'view_count': stats['view_count'],
                    'like_count': stats['like_count'],
                    'comment_count': stats['comment_count'],
                    'share_count': stats['share_count'],
                    'new_score': stats['score'],
                    'score': stats['score'],
                    'already_viewed': False
                }
        except Exception as e:
            print("increase_view_count error:", e)
            return {'view_count': 0, 'like_count': 0, 'comment_count': 0, 'new_score': 0, 'already_viewed': False}

    def toggle_like(self, contest_id, target_id, like_user_id):
        if self.is_contest_closed(contest_id):
            return {'success': False, 'is_ended': True, 'message': '마감(종료)된 콘테스트 회차에는 좋아요를 누를 수 없습니다.'}

        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        
        if not self.is_user_exists(like_user_id):
            self.register_user(like_user_id, like_user_id)

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ROUND_NO FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND (ROUND_NO = %s OR ENT_USER_ID = %s)
                    ORDER BY ENT_DT DESC LIMIT 1
                """, (contest_id, target_id, target_id))
                r_info = cur.fetchone()
                if not r_info:
                    conn.close()
                    return {'success': False, 'message': '출전 게시물을 찾을 수 없습니다.'}
                round_no = r_info['ROUND_NO']

                cur.execute("""
                    SELECT 1 FROM pst_contest_like
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND LIKE_USER_ID = %s
                """, (contest_id, round_no, like_user_id))
                exists = cur.fetchone()

                # 1. DB에 먼저 저장 (추가 또는 삭제)
                if exists:
                    cur.execute("""
                        DELETE FROM pst_contest_like
                        WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND LIKE_USER_ID = %s
                    """, (contest_id, round_no, like_user_id))
                    is_liked = False
                else:
                    cur.execute("""
                        INSERT INTO pst_contest_like (CONTEST_ROUND, ROUND_NO, LIKE_USER_ID)
                        VALUES (%s, %s, %s)
                    """, (contest_id, round_no, like_user_id))
                    is_liked = True

                # 2, 3, 4. DB에서 3요소 재조회 -> 점수 계산 -> DB 업데이트 -> 최종 DB 조회
                stats = self.sync_and_get_post_stats(cur, contest_id, round_no)
                conn.commit()
                conn.close()

                return {
                    'success': True,
                    'is_liked': is_liked,
                    'like_count': stats['like_count'],
                    'view_count': stats['view_count'],
                    'comment_count': stats['comment_count'],
                    'new_score': stats['score'],
                    'score': stats['score']
                }
        except Exception as e:
            print("toggle_like error:", e)
            return {'success': False, 'message': str(e)}

    def trigger_event(self, post_id, event_type, user_id=None, **kwargs):
        contest_id = 1
        target_id = str(post_id)
        if '_' in str(post_id):
            parts = str(post_id).split('_', 1)
            if parts[0].isdigit():
                contest_id = int(parts[0])
                target_id = parts[1]

        if self.is_contest_closed(contest_id):
            return {'success': False, 'is_ended': True, 'message': '마감(종료)된 콘테스트 회차에는 평가 이벤트에 참여할 수 없습니다.'}

        if event_type == 'view':
            res_vw = self.increase_view_count(contest_id, target_id, view_user_id=user_id)
            return {
                'success': True,
                'action': 'view',
                'view_count': res_vw.get('view_count', 0),
                'like_count': res_vw.get('like_count', 0),
                'comment_count': res_vw.get('comment_count', 0),
                'share_count': res_vw.get('share_count', 0),
                'new_score': res_vw.get('new_score', 0),
                'score': res_vw.get('score', 0),
                'is_viewed': True
            }
        elif event_type == 'share':
            conn = self.get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT ROUND_NO, COALESCE(SHARE_CNT, 0) AS SHARE_CNT
                            FROM pst_contest_round
                            WHERE CONTEST_ROUND = %s AND (ROUND_NO = %s OR ENT_USER_ID = %s)
                            ORDER BY ENT_DT DESC LIMIT 1
                        """, (contest_id, target_id, target_id))
                        r_info = cur.fetchone()
                        if r_info:
                            r_no = r_info['ROUND_NO']
                            new_share_cnt = r_info['SHARE_CNT'] + 1
                            stats = self.sync_and_get_post_stats(cur, contest_id, r_no, share_cnt_override=new_share_cnt)
                            conn.commit()
                            conn.close()
                            return {
                                'success': True,
                                'action': 'share',
                                'share_count': stats['share_count'],
                                'view_count': stats['view_count'],
                                'like_count': stats['like_count'],
                                'comment_count': stats['comment_count'],
                                'new_score': stats['score'],
                                'score': stats['score'],
                                'is_shared': True
                            }
                except Exception as e:
                    print("trigger_event share error:", e)
                    if conn:
                        conn.close()
        elif event_type in ('like', 'unlike', 'toggle_like'):
            if not user_id:
                return {'success': False, 'message': '로그인이 필요합니다.'}
            return self.toggle_like(contest_id, target_id, user_id)
        return {'success': True}

    def add_comment(self, contest_id, target_id, cmt_user_id, comment_text):
        if self.is_contest_closed(contest_id):
            return {'success': False, 'is_ended': True, 'message': '마감(종료)된 콘테스트 회차에는 댓글을 추가할 수 없습니다.'}

        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}
        
        if not self.is_user_exists(cmt_user_id):
            self.register_user(cmt_user_id, cmt_user_id)

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ROUND_NO FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND (ROUND_NO = %s OR ENT_USER_ID = %s)
                    ORDER BY ENT_DT DESC LIMIT 1
                """, (contest_id, target_id, target_id))
                r_info = cur.fetchone()
                if not r_info:
                    conn.close()
                    return {'success': False, 'message': '출전 게시물을 찾을 수 없습니다.'}
                round_no = r_info['ROUND_NO']

                # 1. DB에 댓글 먼저 저장
                cur.execute("""
                    INSERT INTO pst_contest_cmt (CONTEST_ROUND, ROUND_NO, CMT_USER_ID, CMT)
                    VALUES (%s, %s, %s, %s)
                """, (contest_id, round_no, cmt_user_id, comment_text))

                # 2, 3, 4. DB에서 3요소 재조회 -> 점수 계산 -> DB 업데이트 -> 최종 DB 조회
                stats = self.sync_and_get_post_stats(cur, contest_id, round_no)
                conn.commit()
                conn.close()

                return {
                    'success': True,
                    'stats': stats,
                    'view_count': stats['view_count'],
                    'like_count': stats['like_count'],
                    'comment_count': stats['comment_count'],
                    'score': stats['score']
                }
        except Exception as e:
            print("add_comment error:", e)
            err_str = str(e)
            if "1062" in err_str or "Duplicate entry" in err_str:
                return {'success': False, 'message': '한 게시물에 한 회원은 단 한번만 댓글 등록 가능합니다.'}
            return {'success': False, 'message': str(e)}

    def delete_comment(self, contest_id, target_id, cmt_user_id):
        if self.is_contest_closed(contest_id):
            return {'success': False, 'is_ended': True, 'message': '마감(종료)된 콘테스트 회차에서는 댓글을 삭제할 수 없습니다.'}

        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ROUND_NO FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s AND (ROUND_NO = %s OR ENT_USER_ID = %s)
                    ORDER BY ENT_DT DESC LIMIT 1
                """, (contest_id, target_id, target_id))
                r_info = cur.fetchone()
                if not r_info:
                    conn.close()
                    return {'success': False, 'message': '출전 게시물을 찾을 수 없습니다.'}
                round_no = r_info['ROUND_NO']

                # 댓글 삭제
                cur.execute("""
                    DELETE FROM pst_contest_cmt
                    WHERE CONTEST_ROUND = %s AND ROUND_NO = %s AND CMT_USER_ID = %s
                """, (contest_id, round_no, cmt_user_id))

                # 3요소 재조회 및 동기화
                stats = self.sync_and_get_post_stats(cur, contest_id, round_no)
                conn.commit()
                conn.close()

                return {
                    'success': True,
                    'stats': stats,
                    'view_count': stats['view_count'],
                    'like_count': stats['like_count'],
                    'comment_count': stats['comment_count'],
                    'score': stats['score']
                }
        except Exception as e:
            print("delete_comment error:", e)
            return {'success': False, 'message': str(e)}

    def get_hall_of_fame(self, contest_id=None):
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                if not contest_id:
                    cur.execute("""
                        SELECT ca.CONTEST_ROUND 
                        FROM pst_contest_award ca
                        JOIN pst_contest c ON ca.CONTEST_ROUND = c.CONTEST_ROUND
                        WHERE c.CONTEST_STAT = 'G001C002'
                        ORDER BY ca.CONTEST_ROUND DESC 
                        LIMIT 1
                    """)
                    r = cur.fetchone()
                    contest_id = r['CONTEST_ROUND'] if r else None

                if not contest_id:
                    conn.close()
                    return []

                cur.execute("""
                    SELECT 
                        ca.CONTEST_ROUND,
                        ca.ROUND_NO,
                        CONCAT(ca.CONTEST_ROUND, '_', ca.ROUND_NO) AS post_id,
                        CONCAT(ca.CONTEST_ROUND, '_', ca.ROUND_NO) AS POST_ID,
                        ca.AWARD_PART,
                        ca.AWARD_CD,
                        COALESCE(ca.KIND_CD, r.KIND_CD) AS KIND_CD,
                        COALESCE(a.AWARD_NM, '당선작') AS AWARD_NM,
                        a.BADGE_IMG_PATH_FILE,
                        ca.SCORE,
                        ca.RANKING,
                        ca.VW_CNT,
                        ca.LIKE_CNT,
                        ca.CMT_CNT,
                        ca.VW_CNT AS view_count,
                        ca.LIKE_CNT AS like_count,
                        ca.CMT_CNT AS comment_count,
                        r.PET_NM,
                        COALESCE(k.KIND_NM, '반려동물') AS KIND_NM,
                        k.KIND_CLASS,
                        r.TITLE,
                        r.CONTS AS content,
                        r.CONTS AS CONTS,
                        DATE_FORMAT(r.ENT_DT, '%%Y-%%m-%%d %%H:%%i:%%s') AS created_at,
                        COALESCE(NULLIF(r.PHT_FILE_PATH1, ''), '/static/image/paw/default_pet.jpg') AS IMAGE_PATH,
                        COALESCE(NULLIF(r.PHT_FILE_PATH2, ''), r.PHT_FILE_PATH1, '/static/image/paw/default_pet.jpg') AS popup_image_path,
                        u.USER_ID,
                        COALESCE(u.NK_NM, ca.ENT_USER_ID) AS NK_NM,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS PROFILE_URL,
                        -- 호환용
                        ca.CONTEST_ROUND AS contest_id,
                        ca.ROUND_NO AS round_no,
                        t.THEME_NM AS contest_title,
                        ca.AWARD_PART AS award_part,
                        ca.AWARD_CD AS award_cd,
                        COALESCE(a.AWARD_NM, '당선작') AS prize_name,
                        a.BADGE_IMG_PATH_FILE AS badge_img,
                        ca.SCORE AS score,
                        ca.RANKING AS ranking,
                        r.PET_NM AS pet_name,
                        COALESCE(k.KIND_NM, '반려동물') AS pet_type,
                        r.TITLE AS title,
                        COALESCE(NULLIF(r.PHT_FILE_PATH1, ''), '/static/image/paw/default_pet.jpg') AS image_path,
                        u.USER_ID AS user_id,
                        COALESCE(u.NK_NM, ca.ENT_USER_ID) AS user_nickname,
                        COALESCE(u.PROFILE_URL, '/static/image/profile/default_profile.png') AS user_profile
                    FROM pst_contest_award ca
                    LEFT JOIN pst_contest c ON ca.CONTEST_ROUND = c.CONTEST_ROUND
                    LEFT JOIN pst_theme t ON c.THEME_CD = t.THEME_CD
                    LEFT JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                    LEFT JOIN pst_contest_round r ON ca.CONTEST_ROUND = r.CONTEST_ROUND AND ca.ROUND_NO = r.ROUND_NO
                    LEFT JOIN pst_user u ON ca.ENT_USER_ID = u.USER_ID
                    LEFT JOIN pst_pet_kind k ON COALESCE(ca.KIND_CD, r.KIND_CD) = k.KIND_CD
                    WHERE ca.CONTEST_ROUND = %s
                    ORDER BY ca.AWARD_PART ASC, ca.KIND_CD ASC, ca.RANKING ASC
                """, (contest_id,))
                winners = cur.fetchall()

                if winners:
                    for w in winners:
                        w_c_id = w['CONTEST_ROUND']
                        w_r_no = w['ROUND_NO']
                        cur.execute("""
                            SELECT 
                                ca.AWARD_PART,
                                ca.AWARD_CD,
                                COALESCE(a.AWARD_NM, '당선작') AS AWARD_NM,
                                a.BADGE_IMG_PATH_FILE,
                                ca.RANKING
                            FROM pst_contest_award ca
                            LEFT JOIN pst_award a ON ca.AWARD_CD = a.AWARD_CD
                            WHERE ca.CONTEST_ROUND = %s AND ca.ROUND_NO = %s
                            ORDER BY ca.AWARD_PART ASC, ca.RANKING ASC
                        """, (w_c_id, w_r_no))
                        w_awards = cur.fetchall()
                        w_awards_list = []
                        for wa in w_awards:
                            wb_file = wa.get('BADGE_IMG_PATH_FILE') or wa.get('AWARD_CD') or ''
                            if wb_file and not wb_file.startswith('/') and not wb_file.startswith('http'):
                                wb_fn = wb_file.split('/')[-1]
                                if not wb_fn.lower().endswith(('.png', '.jpg', '.svg', '.jpeg')):
                                    wb_fn += '.png'
                                wb_url = f'/static/image/badge/{wb_fn}'
                            else:
                                wb_url = wb_file or '/static/image/badge/P001A101.png'

                            wb_url = wb_url.replace('.webp', '.png')

                            w_awards_list.append({
                                'award_part': wa['AWARD_PART'],
                                'award_part_nm': '전체부문' if wa['AWARD_PART'] == 'G002P001' else '품종부문',
                                'award_cd': wa['AWARD_CD'],
                                'award_nm': wa['AWARD_NM'],
                                'badge_img': wb_url,
                                'ranking': wa['RANKING']
                            })
                        w['awards'] = w_awards_list

                conn.close()
                return winners
        except Exception as e:
            print("get_hall_of_fame error:", e)
            return []

service = PawStarService()
