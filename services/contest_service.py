"""
Paw Star Contest & Ranking Service
"""

from datetime import datetime, timedelta
import random
import pymysql
from config import db_config

class PawStarService:
    def __init__(self):
        # 100% DB Direct Query 구동을 위한 물리 테이블 점검
        self._ensure_tables()

    def get_db_connection(self):
        try:
            return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            print("DB Connection Error:", e)
            return None

    def _ensure_tables(self):
        """ DB 물리 테이블 자동 점검 및 마이그레이션 보장 """
        conn = self.get_db_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                # 1. POST_VIEW_LOG
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS POST_VIEW_LOG (
                        VIEW_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
                        POST_ID BIGINT NOT NULL,
                        USER_ID VARCHAR(50) NOT NULL,
                        CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY uk_view_post_user (POST_ID, USER_ID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                # 2. POST_LIKE_LOG
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS POST_LIKE_LOG (
                        LIKE_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
                        POST_ID BIGINT NOT NULL,
                        USER_ID VARCHAR(100) NOT NULL,
                        CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY uk_like_post_user (POST_ID, USER_ID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                        SHARE_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
                        POST_ID BIGINT NOT NULL,
                        USER_ID VARCHAR(100) NOT NULL,
                        CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY uk_share_post_user (POST_ID, USER_ID)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                # 4. post_comment
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS post_comment (
                        comment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        post_id BIGINT NOT NULL,
                        user_id VARCHAR(100) NOT NULL,
                        user_nickname VARCHAR(50),
                        user_profile VARCHAR(255),
                        content TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        KEY idx_post_id (post_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("SHOW TABLES LIKE 'USER_BADGE'")
                if cur.fetchone():
                    cur.execute("SHOW COLUMNS FROM USER_BADGE LIKE 'CONTEST_ID'")
                    if not cur.fetchone():
                        try:
                            cur.execute("ALTER TABLE USER_BADGE ADD COLUMN CONTEST_ID INT NOT NULL AFTER USER_ID")
                        except Exception as alter_e:
                            print("USER_BADGE alter error:", alter_e)

                cur.execute("SHOW COLUMNS FROM USERS LIKE 'LAST_LOGIN_AT'")
                if not cur.fetchone():
                    try:
                        cur.execute("ALTER TABLE USERS ADD COLUMN LAST_LOGIN_AT DATETIME DEFAULT CURRENT_TIMESTAMP")
                    except Exception as err_u1:
                        print("USERS LAST_LOGIN_AT alter error:", err_u1)

                cur.execute("SHOW COLUMNS FROM USERS LIKE 'LOGIN_COUNT'")
                if not cur.fetchone():
                    try:
                        cur.execute("ALTER TABLE USERS ADD COLUMN LOGIN_COUNT INT DEFAULT 0")
                    except Exception as err_u2:
                        print("USERS LOGIN_COUNT alter error:", err_u2)

                conn.commit()
            conn.close()
        except Exception as e:
            print("Ensure tables error:", e)

    def load_data_from_db(self):
        """ 100% DB Direct Query 구조 호환용 """
        return True

    def get_contests(self):
        """ 100% DB SELECT 콘테스트 목록 """
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT CONTEST_ID as contest_id, TITLE as title, START_DATE as start_date, END_DATE as end_date, STATUS as status, DESCRIPTION as description FROM CONTEST ORDER BY CONTEST_ID DESC")
                rows = cur.fetchall()
                contests = []
                for r in rows:
                    contests.append(self._attach_d_day(r))
                conn.close()
                return contests
        except Exception as e:
            print("get_contests error:", e)
            return []

    def get_closed_contests(self):
        """ 100% DB SELECT 마감된(지난) 명예의 전당 콘테스트 목록 (진행중인 현재회차 제외) """
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT CONTEST_ID as contest_id, TITLE as title, START_DATE as start_date, END_DATE as end_date, STATUS as status, DESCRIPTION as description FROM CONTEST WHERE STATUS = 'CLOSED' ORDER BY CONTEST_ID DESC")
                rows = cur.fetchall()
                contests = []
                for r in rows:
                    contests.append(self._attach_d_day(r))
                conn.close()
                return contests
        except Exception as e:
            print("get_closed_contests error:", e)
            return []

    def get_contest(self, contest_id):
        """ 100% DB SELECT 특정 콘테스트 """
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT CONTEST_ID as contest_id, TITLE as title, START_DATE as start_date, END_DATE as end_date, STATUS as status, DESCRIPTION as description FROM CONTEST WHERE CONTEST_ID = %s", (int(contest_id),))
                r = cur.fetchone()
                conn.close()
                if r:
                    return self._attach_d_day(r)
                return None
        except Exception as e:
            print("get_contest error:", e)
            return None

    def get_current_contest(self):
        """ 100% DB 현재 진행 중인(IN_PROGRESS) 콘테스트 회차 반환 """
        conn = self.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT CONTEST_ID as contest_id, TITLE as title, START_DATE as start_date, END_DATE as end_date, STATUS as status, DESCRIPTION as description FROM CONTEST WHERE STATUS = 'IN_PROGRESS' ORDER BY CONTEST_ID ASC LIMIT 1")
                r = cur.fetchone()
                if not r:
                    cur.execute("SELECT CONTEST_ID as contest_id, TITLE as title, START_DATE as start_date, END_DATE as end_date, STATUS as status, DESCRIPTION as description FROM CONTEST ORDER BY CONTEST_ID ASC LIMIT 1")
                    r = cur.fetchone()
                conn.close()
                if r:
                    return self._attach_d_day(r)
                return None
        except Exception as e:
            print("get_current_contest error:", e)
            return None

    def _attach_d_day(self, contest):
        if not contest:
            return contest
        try:
            from datetime import date, datetime
            raw_start = contest.get('start_date')
            raw_end = contest.get('end_date') or contest.get('start_date')

            if raw_start:
                contest['start_date'] = str(raw_start)[:10]
            if raw_end:
                contest['end_date'] = str(raw_end)[:10]

            if isinstance(raw_end, datetime):
                end_date = raw_end.date()
            elif isinstance(raw_end, date):
                end_date = raw_end
            else:
                end_date = datetime.strptime(str(raw_end)[:10], '%Y-%m-%d').date()

            today = datetime.now().date()
            diff_days = (end_date - today).days
            contest['d_day'] = max(0, diff_days)

            if diff_days > 0:
                contest['d_day_str'] = f"D-{diff_days}"
            elif diff_days == 0:
                contest['d_day_str'] = "D-DAY"
            else:
                contest['d_day_str'] = f"D+{abs(diff_days)}"
        except Exception as e:
            print("_attach_d_day error:", e)
            contest['d_day'] = 5
            contest['d_day_str'] = "D-5"

        # status 맵핑 (영문 코드를 한글 상태 뱃지로 변환)
        st = contest.get('status', 'IN_PROGRESS')
        if st in ['IN_PROGRESS', '진행중', '🔥 진행중']:
            contest['status'] = '진행중'
        elif st in ['SCHEDULED', '예정', '📅 예정']:
            contest['status'] = '예정'
        elif st in ['CLOSED', '종료', '🏁 종료']:
            contest['status'] = '종료'

        return contest

    def get_next_post_id(self):
        """ 100% DB MAX(POST_ID) + 1 생성 """
        conn = self.get_db_connection()
        if not conn:
            return 101
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(POST_ID) as max_id FROM POST")
                r = cur.fetchone()
                conn.close()
                max_id = (r['max_id'] if r and r['max_id'] else 100)
                return max_id + 1
        except Exception:
            return 101

    def create_post(self, contest_id, user_id, pet_name, pet_type, title, content, file_path, list_file_name, popup_file_name, force_post_id=None):
        """ 100% MySQL DB Direct INSERT 영구 출전 등록 """
        conn = self.get_db_connection()
        if not conn:
            return None

        new_id = force_post_id or self.get_next_post_id()
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        user_nickname = "반려동물집사"
        user_profile = "/static/image/profile/default_profile.png"
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT NICKNAME, PROFILE_IMG FROM USERS WHERE USER_ID = %s", (user_id,))
                u = cur.fetchone()
                if u:
                    user_nickname = u['NICKNAME']
                    user_profile = u['PROFILE_IMG']
                else:
                    cur.execute("INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE NICKNAME=%s", 
                                (user_id, "반려동물집사", user_profile, "사랑하는 아이와 함께해요", "반려동물집사"))
                    conn.commit()

                sql = """
                    INSERT INTO POST (
                        POST_ID, CONTEST_ID, USER_ID, PET_NAME, PET_TYPE, TITLE, CONTENT,
                        FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT, CREATED_AT
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0, %s)
                """
                cur.execute(sql, (new_id, contest_id, user_id, pet_name, pet_type, title, content, file_path, list_file_name, popup_file_name, now_str))
                conn.commit()
            conn.close()

            return {
                'post_id': new_id,
                'contest_id': contest_id,
                'user_id': user_id,
                'pet_name': pet_name,
                'pet_type': pet_type,
                'title': title,
                'content': content,
                'file_path': file_path,
                'list_file_name': list_file_name,
                'popup_file_name': popup_file_name,
                'score': 0,
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'share_count': 0,
                'created_at': now_str,
                'user_nickname': user_nickname,
                'user_profile': user_profile
            }
        except Exception as e:
            print("create_post 100% DB error:", e)
            return None

    def get_posts(self, contest_id=3, sort_type='latest', search_query='', pet_type='all', page=1, per_page=12, user_id=None):
        """ 100% MySQL DB Direct SELECT 피드 목록 인출 """
        conn = self.get_db_connection()
        if not conn:
            return {'posts': [], 'total_count': 0, 'current_page': page, 'total_pages': 1}

        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT 
                        p.POST_ID as post_id,
                        p.CONTEST_ID as contest_id,
                        p.USER_ID as user_id,
                        p.PET_NAME as pet_name,
                        p.PET_TYPE as pet_type,
                        p.TITLE as title,
                        p.CONTENT as content,
                        p.FILE_PATH as file_path,
                        p.LIST_FILE_NAME as list_file_name,
                        p.POPUP_FILE_NAME as popup_file_name,
                        p.SCORE as score,
                        p.VIEW_COUNT as view_count,
                        p.LIKE_COUNT as like_count,
                        p.COMMENT_COUNT as comment_count,
                        p.SHARE_COUNT as share_count,
                        DATE_FORMAT(p.CREATED_AT, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at,
                        COALESCE(u.NICKNAME, '집사') as user_nickname,
                        COALESCE(u.PROFILE_IMG, '/static/image/profile/default_profile.png') as user_profile
                    FROM POST p
                    LEFT JOIN USERS u ON p.USER_ID = u.USER_ID
                    WHERE p.CONTEST_ID = %s
                """
                params = [int(contest_id)]

                if pet_type and pet_type != 'all':
                    sql += " AND p.PET_TYPE LIKE %s"
                    params.append(f"%{pet_type}%")

                if search_query:
                    sql += " AND (p.TITLE LIKE %s OR p.PET_NAME LIKE %s OR p.CONTENT LIKE %s)"
                    q_param = f"%{search_query}%"
                    params.extend([q_param, q_param, q_param])

                if sort_type == 'popular':
                    sql += " ORDER BY p.LIKE_COUNT DESC, p.SCORE DESC, p.POST_ID DESC"
                elif sort_type == 'score':
                    sql += " ORDER BY p.SCORE DESC, p.LIKE_COUNT DESC, p.POST_ID DESC"
                else:
                    sql += " ORDER BY p.POST_ID DESC"

                count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as sub"
                cur.execute(count_sql, params)
                total_row = cur.fetchone()
                total_count = total_row['total'] if isinstance(total_row, dict) else total_row[0]

                offset = (page - 1) * per_page
                sql += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])

                cur.execute(sql, params)
                rows = cur.fetchall()

                posts = []
                for r in rows:
                    pid = r['post_id']
                    r['actions'] = self.get_user_post_actions(pid, user_id)
                    posts.append(r)

                conn.close()

                total_pages = max(1, (total_count + per_page - 1) // per_page)
                return {
                    'posts': posts,
                    'total_count': total_count,
                    'current_page': page,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
        except Exception as e:
            print("get_posts 100% DB error:", e)
            return {'posts': [], 'total_count': 0, 'current_page': page, 'total_pages': 1}

    def trigger_event(self, post_id, event_type, user_id=None):
        """ 100% MySQL DB Direct SQL INSERT / DELETE & 수치 재계산 """
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT USER_ID, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT FROM POST WHERE POST_ID = %s", (post_id,))
                p_row = cur.fetchone()
                if not p_row:
                    conn.close()
                    return {'success': False, 'message': '게시글이 존재하지 않습니다.'}



                today_str = str(datetime.now().date())
                v_cnt = p_row.get('VIEW_COUNT', 0) or 0
                l_cnt = p_row.get('LIKE_COUNT', 0) or 0
                c_cnt = p_row.get('COMMENT_COUNT', 0) or 0
                s_cnt = p_row.get('SHARE_COUNT', 0) or 0

                if event_type == 'view':
                    v_cnt += 1
                    if user_id:
                        try:
                            cur.execute("INSERT IGNORE INTO POST_VIEW_LOG (POST_ID, USER_ID) VALUES (%s, %s)", (post_id, user_id))
                        except Exception:
                            pass

                elif event_type == 'like':
                    l_cnt += 1
                    if user_id:
                        try:
                            cur.execute("INSERT IGNORE INTO POST_LIKE_LOG (POST_ID, USER_ID) VALUES (%s, %s)", (post_id, user_id))
                        except Exception:
                            pass

                elif event_type == 'unlike':
                    l_cnt = max(0, l_cnt - 1)
                    if user_id:
                        try:
                            cur.execute("DELETE FROM POST_LIKE_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                        except Exception:
                            pass

                elif event_type == 'comment':
                    c_cnt += 1

                elif event_type == 'share':
                    s_cnt += 1

                final_score = (v_cnt * 1) + (l_cnt * 5) + (c_cnt * 10) + (s_cnt * 2)

                cur.execute("""
                    UPDATE POST 
                    SET SCORE = %s, VIEW_COUNT = %s, LIKE_COUNT = %s, COMMENT_COUNT = %s, SHARE_COUNT = %s 
                    WHERE POST_ID = %s
                """, (final_score, v_cnt, l_cnt, c_cnt, s_cnt, post_id))

                conn.commit()
                conn.close()

                return {
                    'success': True,
                    'post_id': post_id,
                    'new_score': final_score,
                    'view_count': v_cnt,
                    'like_count': l_cnt,
                    'comment_count': c_cnt,
                    'share_count': s_cnt
                }
        except Exception as ex:
            print("trigger_event 100% DB error:", ex)
            return {'success': False, 'message': str(ex)}

    def get_user_post_actions(self, post_id, user_id=None):
        """ 100% DB Direct SELECT 로그인 회원 전용 영향력 4가지 상태 판별 """
        if not user_id:
            return {
                'is_viewed': False,
                'is_liked': False,
                'is_commented': False,
                'is_shared': False
            }

        is_viewed, is_liked, is_commented, is_shared = False, False, False, False
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) as cnt FROM POST_VIEW_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    r_v = cur.fetchone()
                    if r_v and (r_v['cnt'] if isinstance(r_v, dict) else r_v[0]) > 0: is_viewed = True

                    cur.execute("SELECT COUNT(*) as cnt FROM POST_LIKE_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    r_l = cur.fetchone()
                    if r_l and (r_l['cnt'] if isinstance(r_l, dict) else r_l[0]) > 0: is_liked = True

                    cur.execute("SELECT COUNT(*) as cnt FROM post_comment WHERE post_id = %s AND user_id = %s", (post_id, user_id))
                    r_c = cur.fetchone()
                    if r_c and (r_c['cnt'] if isinstance(r_c, dict) else r_c[0]) > 0: is_commented = True

                    r_s = cur.fetchone()
                    if r_s and (r_s['cnt'] if isinstance(r_s, dict) else r_s[0]) > 0: is_shared = True
                conn.close()
            except Exception as ex:
                print("DB 영향력 직접 조회 예외:", ex)

        return {
            'is_viewed': is_viewed,
            'is_liked': is_liked,
            'is_commented': is_commented,
            'is_shared': is_shared
        }

    def is_user_liked(self, post_id, user_id):
        """ 100% MySQL DB POST_LIKE_LOG 물리 테이블 조회를 통한 좋아요 반영 여부 반환 """
        try:
                total_row = cur.fetchone()
                total_count = total_row['total'] if isinstance(total_row, dict) else total_row[0]

                offset = (page - 1) * per_page
                sql += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])

                cur.execute(sql, params)
                rows = cur.fetchall()

                posts = []
                for r in rows:
                    pid = r['post_id']
                    r['actions'] = self.get_user_post_actions(pid, user_id)
                    posts.append(r)

                conn.close()

                total_pages = max(1, (total_count + per_page - 1) // per_page)
                return {
                    'posts': posts,
                    'total_count': total_count,
                    'current_page': page,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
        except Exception as e:
            print("get_posts 100% DB error:", e)
            return {'posts': [], 'total_count': 0, 'current_page': page, 'total_pages': 1}

    def trigger_event(self, post_id, event_type, user_id=None):
        """ 100% MySQL DB Direct SQL INSERT / DELETE & 수치 재계산 """
        conn = self.get_db_connection()
        if not conn:
            return {'success': False, 'message': 'DB 연결 실패'}

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT USER_ID, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, SHARE_COUNT FROM POST WHERE POST_ID = %s", (post_id,))
                p_row = cur.fetchone()
                if not p_row:
                    conn.close()
                    return {'success': False, 'message': '게시글이 존재하지 않습니다.'}

                if user_id and p_row['USER_ID'] == user_id:
                    conn.close()
                    return {
                        'success': False,
                        'is_owner': True,
                        'message': '본인의 게시물에는 점수 및 카운팅이 반영되지 않습니다.',
                        'post_id': post_id,
                        'new_score': p_row['SCORE'],
                        'view_count': p_row['VIEW_COUNT'],
                        'like_count': p_row['LIKE_COUNT'],
                        'comment_count': p_row['COMMENT_COUNT'],
                        'share_count': p_row['SHARE_COUNT']
                    }

                today_str = str(datetime.now().date())
                v_delta, l_delta, c_delta, s_delta = 0, 0, 0, 0

                if event_type == 'view':
                    if user_id:
                        cur.execute("SELECT COUNT(*) as cnt FROM POST_VIEW_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                        v_cnt = cur.fetchone()['cnt']
                        if v_cnt > 0:
                            conn.close()
                            return {
                                'success': False,
                                'already_viewed': True,
                                'message': '이미 조회가 완료된 게시물입니다.',
                                'post_id': post_id,
                                'new_score': p_row['SCORE'],
                                'view_count': p_row['VIEW_COUNT'],
                                'like_count': p_row['LIKE_COUNT'],
                                'comment_count': p_row['COMMENT_COUNT'],
                                'share_count': p_row['SHARE_COUNT']
                            }
                        cur.execute("INSERT IGNORE INTO POST_VIEW_LOG (POST_ID, USER_ID) VALUES (%s, %s)", (post_id, user_id))
                    v_delta = 1

                elif event_type == 'like':
                    if user_id:
                        cur.execute("INSERT IGNORE INTO POST_LIKE_LOG (POST_ID, USER_ID) VALUES (%s, %s)", (post_id, user_id))
                    l_delta = 1

                elif event_type == 'unlike':
                    if user_id:
                        cur.execute("DELETE FROM POST_LIKE_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    l_delta = -1

                elif event_type == 'comment':
                    c_delta = 1

                elif event_type == 'share':
                    if user_id:
                        pass
                    s_delta = 1

                cur.execute("SELECT COUNT(*) as cnt FROM POST_VIEW_LOG WHERE POST_ID = %s", (post_id,))
                db_v = cur.fetchone()['cnt']

                cur.execute("SELECT COUNT(*) as cnt FROM POST_LIKE_LOG WHERE POST_ID = %s", (post_id,))
                db_l = cur.fetchone()['cnt']

                cur.execute("SELECT COUNT(*) as cnt FROM post_comment WHERE POST_ID = %s", (post_id,))
                db_c = cur.fetchone()['cnt']

                db_s = p_row.get('SHARE_COUNT', 0)

                final_v = max(p_row['VIEW_COUNT'], db_v)
                final_l = max(0, db_l)
                final_c = max(p_row['COMMENT_COUNT'], db_c)
                final_s = max(p_row['SHARE_COUNT'], db_s)
                final_score = (final_v * 1) + (final_l * 5) + (final_c * 10) 

                cur.execute("""
                    UPDATE POST 
                    SET SCORE = %s, VIEW_COUNT = %s, LIKE_COUNT = %s, COMMENT_COUNT = %s, SHARE_COUNT = %s 
                    WHERE POST_ID = %s
                """, (final_score, final_v, final_l, final_c, final_s, post_id))

                cur.execute("""
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        VIEW_COUNT = VIEW_COUNT + VALUES(VIEW_COUNT),
                        LIKE_COUNT = LIKE_COUNT + VALUES(LIKE_COUNT),
                        COMMENT_COUNT = COMMENT_COUNT + VALUES(COMMENT_COUNT),
                        SHARE_COUNT = SHARE_COUNT + VALUES(SHARE_COUNT)
                """, (post_id, today_str, max(0, v_delta), max(0, l_delta), max(0, c_delta), max(0, s_delta)))

                conn.commit()
                conn.close()

                return {
                    'post_id': post_id,
                    'new_score': final_score,
                    'view_count': final_v,
                    'like_count': final_l,
                    'comment_count': final_c,
                    'share_count': final_s
                }
        except Exception as ex:
            print("trigger_event 100% DB error:", ex)
            return {'success': False, 'message': str(ex)}

    def get_user_post_actions(self, post_id, user_id=None):
        """ 100% DB Direct SELECT 로그인 회원 전용 영향력 4가지 상태 판별 """
        if not user_id:
            return {
                'is_viewed': False,
                'is_liked': False,
                'is_commented': False,
                'is_shared': False
            }

        is_viewed, is_liked, is_commented, is_shared = False, False, False, False
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) as cnt FROM POST_VIEW_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    r_v = cur.fetchone()
                    if r_v and (r_v['cnt'] if isinstance(r_v, dict) else r_v[0]) > 0: is_viewed = True

                    cur.execute("SELECT COUNT(*) as cnt FROM POST_LIKE_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    r_l = cur.fetchone()
                    if r_l and (r_l['cnt'] if isinstance(r_l, dict) else r_l[0]) > 0: is_liked = True

                    cur.execute("SELECT COUNT(*) as cnt FROM post_comment WHERE post_id = %s AND user_id = %s", (post_id, user_id))
                    r_c = cur.fetchone()
                    if r_c and (r_c['cnt'] if isinstance(r_c, dict) else r_c[0]) > 0: is_commented = True

                    r_s = cur.fetchone()
                    if r_s and (r_s['cnt'] if isinstance(r_s, dict) else r_s[0]) > 0: is_shared = True
                conn.close()
            except Exception as ex:
                print("DB 영향력 직접 조회 예외:", ex)

        return {
            'is_viewed': is_viewed,
            'is_liked': is_liked,
            'is_commented': is_commented,
            'is_shared': is_shared
        }

    def is_user_liked(self, post_id, user_id):
        """ 100% MySQL DB POST_LIKE_LOG 물리 테이블 조회를 통한 좋아요 반영 여부 반환 """
        try:
            if not user_id:
                return False
            conn = self.get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) as cnt FROM POST_LIKE_LOG WHERE POST_ID = %s AND USER_ID = %s", (post_id, user_id))
                    row = cur.fetchone()
                    conn.close()
                    if row and (row['cnt'] if isinstance(row, dict) else row[0]) > 0:
                        return True
            return False
        except Exception:
            return False

    def get_user_profile(self, user_id='user1'):
        """ 100% MySQL DB Direct SELECT 로 회원 프로필 및 내 게시물/수상내역 인출 """
        if not user_id:
            user_id = 'user1'

        user_info = {
            'user_id': user_id,
            'nickname': '귀여운집사',
            'profile_img': '/static/image/profile/default_profile.png',
            'bio': '세상 모든 반려동물은 사랑입니다 🐾 매일매일 심쿵!',
            'joined_date': '2026-01-15',
            'badges': ['🥇 슈퍼스타 1위', '🥈 라이징스타']
        }
        my_posts = []
        my_awards = []

        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM USERS WHERE USER_ID = %s", (user_id,))
                    u = cur.fetchone()
                    if u:
                        user_info['nickname'] = u.get('NICKNAME') or '집사'
                        user_info['profile_img'] = u.get('PROFILE_IMG') or '/static/image/profile/default_profile.png'
                        user_info['bio'] = u.get('BIO') or ''
                        user_info['joined_date'] = str(u.get('CREATED_AT', '2026-01-15')).split(' ')[0]

                    cur.execute("""
                        SELECT 
                            POST_ID as post_id, CONTEST_ID as contest_id, USER_ID as user_id, PET_NAME as pet_name,
                            PET_TYPE as pet_type, TITLE as title, CONTENT as content,
                            COALESCE(FILE_PATH, '/static/image/paw/2026/07/') as file_path,
                            COALESCE(LIST_FILE_NAME, '3-101_list.webp') as list_file_name,
                            COALESCE(POPUP_FILE_NAME, '3-101_popup.webp') as popup_file_name,
                            SCORE as score, VIEW_COUNT as view_count, LIKE_COUNT as like_count,
                            COMMENT_COUNT as comment_count, SHARE_COUNT as share_count,
                            DATE_FORMAT(CREATED_AT, '%%Y-%%m-%%d') as created_at
                        FROM POST WHERE USER_ID = %s ORDER BY POST_ID DESC
                    """, (user_id,))
                    my_posts = cur.fetchall()

                    cur.execute("""
                        SELECT 
                            w.CONTEST_ID as contest_id, w.POST_ID as post_id, w.USER_ID as user_id,
                            w.AWARD_TYPE as award_type, w.PRIZE_NAME as prize_name,
                            COALESCE(p.PET_NAME, '반려동물') as pet_name,
                            COALESCE(p.PET_TYPE, '🐕 강아지') as pet_type,
                            COALESCE(p.TITLE, '수상 작품') as post_title,
                            COALESCE(p.SCORE, 0) as score
                        FROM CONTEST_WINNER w
                        LEFT JOIN POST p ON w.POST_ID = p.POST_ID
                        WHERE w.USER_ID = %s 
                        ORDER BY w.CONTEST_ID DESC
                    """, (user_id,))
                    my_awards = cur.fetchall()
                conn.close()
            except Exception as e:
                print("get_user_profile DB error:", e)

        my_post_count = len(my_posts)
        total_score = sum(p['score'] for p in my_posts)
        total_likes = sum(p['like_count'] for p in my_posts)

        return {
            'user_info': user_info,
            'stats': {
                'my_post_count': my_post_count,
                'total_score': total_score,
                'total_likes': total_likes,
                'award_count': len(my_awards)
            },
            'my_posts': my_posts,
            'my_awards': my_awards
        }

    def update_user_profile(self, user_id, nickname=None, bio=None, profile_img=None):
        """ 사용자 프로필(닉네임, 한줄소개, 프로필이미지) DB 업데이트 """
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    update_fields = []
                    params = []

                    if nickname is not None and str(nickname).strip():
                        update_fields.append("NICKNAME = %s")
                        params.append(str(nickname).strip())
                    if bio is not None:
                        update_fields.append("BIO = %s")
                        params.append(str(bio).strip())
                    if profile_img is not None and str(profile_img).strip():
                        update_fields.append("PROFILE_IMG = %s")
                        params.append(str(profile_img).strip())

                    if update_fields:
                        params.append(user_id)
                        sql = f"UPDATE USERS SET {', '.join(update_fields)} WHERE USER_ID = %s"
                        cur.execute(sql, tuple(params))
                        
                        if nickname is not None and str(nickname).strip():
                            cur.execute("UPDATE post_comment SET user_nickname = %s WHERE user_id = %s", (str(nickname).strip(), user_id))

                        conn.commit()

                    cur.execute("SELECT USER_ID, NICKNAME, PROFILE_IMG, BIO FROM USERS WHERE USER_ID = %s", (user_id,))
                    u = cur.fetchone()
                conn.close()
                if u:
                    return {
                        'user_id': u['USER_ID'],
                        'nickname': u['NICKNAME'],
                        'profile_img': u['PROFILE_IMG'],
                        'bio': u.get('BIO', '')
                    }
            except Exception as e:
                print("update_user_profile DB error:", e)

        return {'user_id': user_id, 'nickname': nickname or '', 'bio': bio or '', 'profile_img': profile_img or ''}

    def delete_user(self, user_id):
        """ 100% DB DELETE 회원 탈퇴 처리 """
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM USERS WHERE USER_ID = %s", (user_id,))
                    conn.commit()
                conn.close()
            except Exception as e:
                print("delete_user DB error:", e)
        return True

    def close_contest_and_award(self, contest_id):
        """ 회차 종료 상태 변경 100% DB UPDATE """
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE CONTEST SET STATUS = 'CLOSED' WHERE CONTEST_ID = %s", (int(contest_id),))
                    conn.commit()
                conn.close()
            except Exception as e:
                print("close_contest DB error:", e)
        return self.get_hall_of_fame(contest_id)

    def get_hall_of_fame(self, contest_id=2):
        """ 100% MySQL DB Direct JOIN SELECT 명예의 전당 수상자 인출 """
        conn = self.get_db_connection()
        if not conn: return []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        w.CONTEST_ID as contest_id, w.POST_ID as post_id, w.USER_ID as user_id,
                        w.AWARD_TYPE as award_type, w.PRIZE_NAME as prize_name,
                        COALESCE(p.PET_NAME, '반려동물') as pet_name,
                        COALESCE(p.PET_TYPE, '🐕 강아지') as pet_type,
                        COALESCE(p.TITLE, '수상 작품') as post_title,
                        COALESCE(p.FILE_PATH, '/static/image/paw/2026/07/') as file_path,
                        COALESCE(p.LIST_FILE_NAME, '3-101_list.webp') as list_file_name,
                        COALESCE(p.POPUP_FILE_NAME, '3-101_popup.webp') as popup_file_name,
                        CONCAT(COALESCE(p.FILE_PATH, '/static/image/paw/2026/07/'), COALESCE(p.LIST_FILE_NAME, '3-101_list.webp')) as image_path,
                        COALESCE(p.SCORE, 0) as score,
                        COALESCE(p.VIEW_COUNT, 0) as view_count,
                        COALESCE(p.LIKE_COUNT, 0) as like_count,
                        COALESCE(p.COMMENT_COUNT, 0) as comment_count,
                        COALESCE(p.SHARE_COUNT, 0) as share_count,
                        COALESCE(u.NICKNAME, '우승집사') as user_nickname,
                        COALESCE(u.PROFILE_IMG, '/static/image/profile/default_profile.png') as user_profile
                    FROM CONTEST_WINNER w
                    LEFT JOIN POST p ON w.POST_ID = p.POST_ID
                    LEFT JOIN USERS u ON w.USER_ID = u.USER_ID
                    WHERE w.CONTEST_ID = %s
                    ORDER BY CASE 
                        WHEN w.AWARD_TYPE = 'SUPER_STAR' THEN 1
                        WHEN w.AWARD_TYPE = 'RISING_STAR' THEN 2
                        WHEN w.AWARD_TYPE = 'BRIGHT_STAR' THEN 3
                        ELSE 4
                    END, p.SCORE DESC
                """, (int(contest_id),))
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    if r.get('prize_name') and '&' in r['prize_name']:
                        r['prize_name'] = r['prize_name'].split('&')[0].strip()
                    r['score_breakdown'] = f"👀 {r.get('view_count', 0):,}   ❤️ {r.get('like_count', 0):,}   💬 {r.get('comment_count', 0):,}   🔄 {r.get('share_count', 0):,}"
                return rows
        except Exception as e:
            print("get_hall_of_fame DB error:", e)
            return []

    def hash_user_id(self, raw_id):
        if not raw_id:
            return ""
        if len(str(raw_id)) == 64 and all(c in '0123456789abcdefABCDEF' for c in str(raw_id)):
            return str(raw_id).lower()
        import hashlib
        return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

    def google_login_or_register(self, google_id, email=None, default_name=None, picture=None):
        """ 100% MySQL DB Direct SELECT/INSERT 기반 구글 로그인 및 회원가입 """
        raw_user_id = f"google_{google_id}"
        user_id = self.hash_user_id(raw_user_id)
        profile_img = picture if (picture and picture.strip()) else '/static/image/profile/default_profile.png'

        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM USERS WHERE USER_ID = %s", (user_id,))
                    u = cur.fetchone()
                    if not u:
                        import random
                        prefix_list = ['귀여운집사', '행복집사', '초보집사', '댕냥집사', '심쿵집사', '빛나는집사', '러블리집사', '펫스타', '보송보송집사', '말랑말랑집사']
                        random_nickname = f"{random.choice(prefix_list)}_{random.randint(1000, 9999)}"
                        bio = 'PawStar에서 반려동물과 행복한 일상을 나누고 있습니다 🐾'
                        cur.execute("""
                            INSERT INTO USERS (USER_ID, NICKNAME, PROFILE_IMG, BIO, LAST_LOGIN_AT, LOGIN_COUNT)
                            VALUES (%s, %s, %s, %s, NOW(), 1)
                        """, (user_id, random_nickname, profile_img, bio))
                        conn.commit()
                        u = {'USER_ID': user_id, 'NICKNAME': random_nickname, 'PROFILE_IMG': profile_img, 'BIO': bio}
                    else:
                        if picture and picture.strip():
                            cur.execute("""
                                UPDATE USERS 
                                SET PROFILE_IMG = %s, LAST_LOGIN_AT = NOW(), LOGIN_COUNT = COALESCE(LOGIN_COUNT, 0) + 1 
                                WHERE USER_ID = %s
                            """, (profile_img, user_id))
                        else:
                            cur.execute("""
                                UPDATE USERS 
                                SET LAST_LOGIN_AT = NOW(), LOGIN_COUNT = COALESCE(LOGIN_COUNT, 0) + 1 
                                WHERE USER_ID = %s
                            """, (user_id,))
                        conn.commit()
                        if picture and picture.strip():
                            u['PROFILE_IMG'] = profile_img
                conn.close()
                return {
                    'user_id': u['USER_ID'],
                    'nickname': u['NICKNAME'],
                    'profile_img': u['PROFILE_IMG'],
                    'bio': u.get('BIO', '')
                }
            except Exception as e:
                print("google_login_or_register DB error:", e)

        import random
        prefix_list = ['귀여운집사', '행복집사', '초보집사', '댕냥집사', '심쿵집사', '빛나는집사', '러블리집사', '펫스타', '보송보송집사', '말랑말랑집사']
        fallback_nick = f"{random.choice(prefix_list)}_{random.randint(1000, 9999)}"
        return {'user_id': user_id, 'nickname': fallback_nick, 'profile_img': profile_img, 'bio': ''}

    def get_comments_by_post(self, post_id):
        """ 게시물 댓글 목록 조회 """
        conn = self.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT comment_id, post_id, user_id, user_nickname, user_profile, content,
                           DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at
                    FROM post_comment
                    WHERE post_id = %s
                    ORDER BY created_at ASC
                """, (post_id,))
                rows = cur.fetchall()
            conn.close()
            return rows if rows else []
        except Exception as e:
            print("get_comments_by_post DB error:", e)
            if conn:
                conn.close()
            return []

    def add_comment(self, post_id, user_nickname, content, user_profile=None, user_id=None):
        """ 게시물 한줄 댓글 추가 및 1회 한정 +10점 이벤트 처리 """
        if not user_id:
            user_id = 'anonymous'
        
        conn = self.get_db_connection()
        if not conn:
            return None, "DB연결 오류"
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO post_comment (post_id, user_id, user_nickname, user_profile, content)
                    VALUES (%s, %s, %s, %s, %s)
                """, (post_id, user_id, user_nickname, user_profile, content))
                comment_id = cur.lastrowid
                conn.commit()
            conn.close()
            
            # 이벤트(점수 및 수치 증가) 트리거
            event_res = self.trigger_event(post_id, 'comment', user_id=user_id)
            
            comment_data = {
                'comment_id': comment_id,
                'post_id': post_id,
                'user_id': user_id,
                'user_nickname': user_nickname,
                'user_profile': user_profile,
                'content': content
            }
            return comment_data, event_res
        except Exception as e:
            print("add_comment DB error:", e)
            if conn:
                conn.close()
            return None, str(e)

# 100% Pure MySQL DB Direct 서비스 싱글톤 객체 생성
service = PawStarService()
