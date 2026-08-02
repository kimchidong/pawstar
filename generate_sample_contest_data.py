# -*- coding: utf-8 -*-
"""
Paw Star 콘테스트 샘플 데이터 자동 생성기 (generate_sample_contest_data.py)
/static/sample_image 폴더의 20개 이미지 파일들을 활용하여
지난 회차 2개(제1회, 제2회) 및 현재 진행 중 회차(제3회)의 
풍성한 출전 포스트, 좋아요, 댓글, 조회수 및 명예의 전당 수상 내역을 자동 시딩합니다.
"""

import os
import sys
import io
import random
import pymysql
from datetime import datetime, timedelta
from config import db_config

# Windows 콘솔 인코딩 출력 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_db_connection():
    return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)

def run_seed():
    print("=" * 65)
    print("🐾 Paw Star - 샘플 콘테스트 데이터 자동 시딩 시작")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_img_dir = os.path.join(base_dir, 'static', 'sample_image')
    
    if not os.path.exists(sample_img_dir):
        print(f"❌ 샘플 이미지 디렉터리를 찾을 수 없습니다: {sample_img_dir}")
        return

    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    image_files = [f for f in os.listdir(sample_img_dir) if f.lower().endswith(valid_exts)]
    image_files.sort()

    if not image_files:
        print(f"❌ '{sample_img_dir}' 디렉터리에 샘플 이미지가 없습니다.")
        return

    print(f"📸 발견된 샘플 이미지 개수: {len(image_files)}개 ({', '.join(image_files[:5])}...)\n")

    conn = get_db_connection()
    if not conn:
        print("❌ DB 연결 실패!")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # 1. 샘플 사용자 (pst_user) 시딩
            users_list = [
                ('user_poppie', '뽀삐아빠', '/static/image/profile/default_profile.png', '골든리트리버 뽀삐와 살고 있어요 🦮'),
                ('user_navi', '냥냥집사', '/static/image/profile/default_profile.png', '귀여운 아비시니안 나비의 하루 🐈'),
                ('user_mozzi', '햄찌마스터', '/static/image/profile/default_profile.png', '볼빵빵 햄찌 모찌 🐹'),
                ('user_angdoo', '앵두네', '/static/image/profile/default_profile.png', '노래하는 모란앵무 앵두 🦜'),
                ('user_rabbit', '토끼농장', '/static/image/profile/default_profile.png', '깡총깡총 토순이 집사 🐇'),
                ('user_hedgehog', '도치사랑', '/static/image/profile/default_profile.png', '동글동글 고슴도치 또치 🦔'),
                ('user_lizard', '파충류매니아', '/static/image/profile/default_profile.png', '멋쟁이 도마뱀 드래곤 🦎'),
                ('user_fish', '어항속세계', '/static/image/profile/default_profile.png', '알록달록 열대어 집사 🐠'),
                ('user_ferret', '족제비길들이기', '/static/image/profile/default_profile.png', '말썽꾸러기 페럿 🦦'),
                ('user_horse', '카우보이', '/static/image/profile/default_profile.png', '당당한 말 적토마 🐴'),
                ('user_pig', '꿀꿀이네', '/static/image/profile/default_profile.png', '복스럽고 앙증맞은 미니피그 🐷'),
                ('user_choco', '초코맘', '/static/image/profile/default_profile.png', '귀여운 푸들 초코 🐩'),
                ('user_cheese', '치즈집사', '/static/image/profile/default_profile.png', '노란 털 뭉치 치즈 🧀'),
                ('user_mango', '망고네', '/static/image/profile/default_profile.png', '상큼발랄 스코티시 망고 🥭'),
                ('user_gureum', '구름아빠', '/static/image/profile/default_profile.png', '솜사탕 비숑 구름이 ☁️')
            ]

            cur.execute("DELETE FROM pst_user WHERE USER_ID LIKE 'user_%';")
            for u_id, nk, p_img, bio in users_list:
                cur.execute("""
                    INSERT INTO pst_user (USER_ID, NK_NM, PROFILE_URL, LGN_CNT, LGN_DT, JOIN_DT)
                    VALUES (%s, %s, %s, 1, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE NK_NM=%s, PROFILE_URL=%s
                """, (u_id, nk, p_img, nk, p_img))

            print("✅ 사용자(pst_user) 시딩 완료!")

            # 2. 테마 (pst_theme) 시딩
            themes = [
                ('T001', '06', '🌊 제1회 썸머 파라다이스 펫 콘테스트', '무더위를 싹 씻어줄 시원하고 러블리한 썸머 펫 스타 🏖️', '/static/image/banner/banner1.jpg'),
                ('T002', '07', '🏖️ 제2회 한여름 밤의 바캉스 펫 챔피언십', '뜨거운 여름 열기보다 더 핫한 인플루언서 펫 축제 ⭐', '/static/image/banner/banner2.jpg'),
                ('T003', '08', '🍁 제3회 가을 힐링 & 감성 펫스타 콘테스트', '마음까지 넉넉해지는 풍성한 가을 둥글둥글 귀요미들 🍂', '/static/image/banner/banner3.jpg'),
            ]
            for t_cd, mnth, t_nm, t_ment, t_banner in themes:
                cur.execute("""
                    INSERT INTO pst_theme (THEME_CD, MNTH, THEME_NM, THEME_MENT, BANNER_IMG_FILE_PATH)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE MNTH=%s, THEME_NM=%s, THEME_MENT=%s, BANNER_IMG_FILE_PATH=%s
                """, (t_cd, mnth, t_nm, t_ment, t_banner, mnth, t_nm, t_ment, t_banner))

            # 3. 콘테스트 회차 (pst_contest) 시딩 (지난 회차 2개 + 진행 중 회차 1개)
            contests = [
                (1, 'T001', '2026-06-01 00:00:00', '2026-06-30 23:59:59', 'G001C002'), # 지난 회차 1 (종료)
                (2, 'T002', '2026-07-01 00:00:00', '2026-07-31 23:59:59', 'G001C002'), # 지난 회차 2 (종료)
                (3, 'T003', '2026-08-01 00:00:00', '2026-08-31 23:59:59', 'G001C001'), # 현재 진행 회차 3 (진행중)
            ]
            cur.execute("DELETE FROM pst_contest WHERE CONTEST_ROUND IN (1, 2, 3);")
            for c_round, t_cd, st_dt, ed_dt, stat in contests:
                cur.execute("""
                    INSERT INTO pst_contest (CONTEST_ROUND, THEME_CD, ST_DT, ED_DT, CONTEST_STAT)
                    VALUES (%s, %s, %s, %s, %s)
                """, (c_round, t_cd, st_dt, ed_dt, stat))

            print("✅ 콘테스트 회차(pst_contest) 시딩 완료! (1회차: 종료, 2회차: 종료, 3회차: 진행중)")

            # 4. 품종 정보 (pst_pet_kind) 확보
            cur.execute("SELECT KIND_CD, KIND_NM FROM pst_pet_kind;")
            pet_kinds_rows = cur.fetchall()
            kind_map = {row['KIND_NM']: row['KIND_CD'] for row in pet_kinds_rows}
            kind_list = list(kind_map.keys()) if kind_map else ['🐕 강아지', '🐈 고양이', '🐹 햄스터', '🦜 앵무새', '🐇 토끼', '🐴 말/큰동물', '🐷 돼지/피그']

            # 메타데이터 미리 정의 (20개 이미지와 매핑)
            pet_metadata = [
                {"name": "뽀삐", "kind": "🐕 강아지", "title": "햇살 가득 머금은 웃는 모습 ☀️", "content": "오늘 산책하면서 찍은 인생샷입니다! 카메라만 대면 이렇게 예쁘게 웃어줘요 🐶❤️"},
                {"name": "나비", "kind": "🐈 고양이", "title": "식빵 굽는 보송보송 찹쌀떡 🍞", "content": "골골송 부르며 골골 대는 모습이 너무 사랑스러워요~ 집사 심장 폭발 중!"},
                {"name": "모찌", "kind": "🐹 햄스터", "title": "해바라기씨 볼빵빵 탐식가 🌻", "content": "볼주머니 가득 해바라기씨 넣고 뽈뽈거리는 우리 모찌 자랑해봅니다 🐹✨"},
                {"name": "앵두", "kind": "🦜 앵무새/조류", "title": "노래하는 알록달록 무지개 깃털 🌈", "content": "아침마다 안녕~ 하고 인사해주는 미모의 앵무새 앵두예요 🦜🎵"},
                {"name": "토순이", "kind": "🐇 토끼", "title": "오물오물 당근 먹방 라이브 🥕", "content": "당근 조각을 옴뇸뇸 맛있게 먹는 귀여운 토끼 토순이의 심쿵 포인트!"},
                {"name": "또치", "kind": "🦔 고슴도치", "title": "밤송이 속에 숨은 핑크 코 귀요미 🦔", "content": "처음엔 경계하다가 밀웜 보여주니 쏙 얼굴 내미는 귀염둥이 또치!"},
                {"name": "드래곤", "kind": "🦎 파충류/도마뱀", "title": "햇볕 쬐며 여유를 즐기는 카리스마 🦎", "content": "멋진 주황빛 비늘을 자랑하는 우리 도마뱀 드래곤입니다."},
                {"name": "네모", "kind": "🐠 어류/관상어", "title": "어항 속에서 환하게 헤엄치는 니모 🐠", "content": "물속을 살랑살랑 누비는 우리 집 귀염둥이 열대어 네모예요!"},
                {"name": "페리", "kind": "🦦 페럿", "title": "이리저리 뽈뽈거리는 족제비 귀요미 🦦", "content": "잠시도 가만있지 않는 장난꾸러기 페리! 자는 모습은 천사랍니다."},
                {"name": "적토마", "kind": "🐴 말/큰동물", "title": "푸른 잔디밭을 달리는 당당한 자태 🐴", "content": "바람을 가르며 힘차게 뛰어노는 늠름하고 아름다운 적토마!"},
                {"name": "꿀꿀이", "kind": "🐷 돼지/피그", "title": "복스러운 핑크빛 귀염둥이 미니피그 🐷", "content": "밥 먹을 때 가장 행복한 표정을 짓는 꿀꿀이 자랑합니다!"},
                {"name": "몽이", "kind": "🐕 강아지", "title": "복실복실 몽몽이의 솜사탕 매력 ☁️", "content": "미용하고 와서 보송보송함 그 자체입니다. 인기가 폭발했어요!"},
                {"name": "루이", "kind": "🐈 고양이", "title": "에메랄드빛 눈동자의 캣초딩 💎", "content": "창밖 구경에 푹 빠진 루이입니다. 옆태 라인이 정말 예술이지 않나요?"},
                {"name": "초코", "kind": "🐕 강아지", "title": "애착 인형 품에 꼭 안고 숙면 중 🧸", "content": "최애 인형을 끌어안고 단잠에 빠진 우리 초코! 보는 내내 힐링됩니다."},
                {"name": "두부", "kind": "🐕 강아지", "title": "말랑말랑 말티즈 뭉클 귀요미 🤍", "content": "간식 소리만 들으면 귀가 쫑긋해지는 두부의 심쿵 눈빛 발사!"},
                {"name": "망고", "kind": "🐈 고양이", "title": "노란 털 뭉치 햇살 낮잠 타이밍 🍊", "content": "따스한 햇살 아래서 나른하게 졸고 있는 오렌지빛 망고입니다."},
                {"name": "코코", "kind": "🐕 강아지", "title": "산책 나가기 전 무한 꼬리 헬리콥터 🚁", "content": "리드줄만 들면 신나서 헬리콥터처럼 꼬리를 흔드는 귀염둥이 코코!"},
                {"name": "치즈", "kind": "🐈 고양이", "title": "상자 속 쏙 들어간 식빵 치즈 🧀", "content": "아무리 작은 택배 상자라도 자기 몸을 구겨 넣는 신기한 치즈!"},
                {"name": "구름", "kind": "🐕 강아지", "title": "폭신폭신 구름이의 하트 눈빛 ☁️", "content": "퇴근하고 집에 오면 제일 먼저 반겨주는 내 사랑 구름이의 멍뭉미!"},
                {"name": "보리", "kind": "🐕 강아지", "title": "바람을 가르며 달리는 맑은 미소 🌾", "content": "잔디밭을 신나게 달리며 스트레스 제로가 된 보리의 맑고 깨끗한 웃음!"}
            ]

            sample_comments = [
                "너무 사랑스럽네요! 투표 하트 꾹 누르고 갑니다 ❤️",
                "우와~ 인형 아닌가요? 심쿵사할 뻔했어요 🥺✨",
                "표정이 어쩜 이렇게 예쁘죠? 이번 콘테스트 우승 가자!",
                "눈동자가 정말 보석 같아요~ 응원합니다! 💎",
                "보는 내내 미소가 절로 나네요 ㅎㅎ 건강하게 잘 자라렴 🐾",
                "우리아이보다 더 귀여운 것 같아요! 완전 스타감이네요 👍",
                "힐링 제대로 하고 갑니다~ 1등 응원해요 👑",
                "털 복실복실해서 너무 감촉 좋아 보여요! 🥰",
                "완전 심쿵 포인트! 매일 보러 올게요~",
                "표정이 너무 해맑아서 저까지 행복해지네요 😊"
            ]

            # 5. 기존 참가 데이터 & 하위 테이블 정리
            cur.execute("DELETE FROM pst_contest_award WHERE CONTEST_ROUND IN (1, 2, 3);")
            cur.execute("DELETE FROM pst_contest_cmt WHERE CONTEST_ROUND IN (1, 2, 3);")
            cur.execute("DELETE FROM pst_contest_like WHERE CONTEST_ROUND IN (1, 2, 3);")
            cur.execute("DELETE FROM pst_contest_vw WHERE CONTEST_ROUND IN (1, 2, 3);")
            cur.execute("DELETE FROM pst_contest_round WHERE CONTEST_ROUND IN (1, 2, 3);")

            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

            total_posts_created = 0

            # 6. 각 회차별 (회차 1, 2, 3) 20개 게시물 시딩
            for c_round in [1, 2, 3]:
                print(f"\n🚀 [회차 #{c_round}] 시딩 진행 중...")
                
                # 회차 1, 2는 종료 회차이므로 무작위 점수 선별
                # 회차별로 이미지 20개를 섞어서 생성
                shuffled_indices = list(range(len(image_files)))
                random.seed(c_round * 100 + 7) # 회차별로 다채로운 조합
                random.shuffle(shuffled_indices)

                for r_idx, idx in enumerate(shuffled_indices):
                    round_no = r_idx + 1
                    img_name = image_files[idx]
                    meta = pet_metadata[idx]
                    user = users_list[idx % len(users_list)]

                    user_id = user[0]
                    pet_name = meta["name"]
                    kind_nm = meta["kind"]
                    
                    # KIND_CD 찾기
                    kind_cd = None
                    for k_name, k_code in kind_map.items():
                        if pet_name in k_name or kind_nm.split()[1] in k_name or k_name.split()[0] in kind_nm:
                            kind_cd = k_code
                            break
                    if not kind_cd:
                        kind_cd = list(kind_map.values())[0] if kind_map else 'K001'

                    title = f"[{c_round}회차] {meta['title']}"
                    conts = meta['content']
                    file_path = f"/static/sample_image/{img_name}"

                    # 회차별 시간 설정
                    if c_round == 1:
                        base_dt = datetime(2026, 6, 1) + timedelta(days=random.randint(0, 25), hours=random.randint(0, 23))
                    elif c_round == 2:
                        base_dt = datetime(2026, 7, 1) + timedelta(days=random.randint(0, 25), hours=random.randint(0, 23))
                    else:
                        base_dt = datetime.now() - timedelta(days=random.randint(0, 2), hours=random.randint(0, 12))

                    # 1등/2등/3등 상위 점수 편차 부여
                    if round_no <= 3:
                        vw_cnt = random.randint(250, 450)
                        like_cnt = random.randint(120, 250)
                        cmt_cnt = random.randint(15, 35)
                    else:
                        vw_cnt = random.randint(30, 200)
                        like_cnt = random.randint(5, 90)
                        cmt_cnt = random.randint(1, 12)

                    score = (vw_cnt * 1) + (like_cnt * 5) + (cmt_cnt * 10)

                    # pst_contest_round INSERT
                    cur.execute("""
                        INSERT INTO pst_contest_round (
                            CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, PET_NM, TITLE, CONTS,
                            PHT_FILE_PATH1, PHT_FILE_PATH2, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, ENT_DT
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (c_round, round_no, user_id, kind_cd, pet_name, title, conts, file_path, file_path, vw_cnt, like_cnt, cmt_cnt, score, base_dt))

                    # 하위 조회수 레코드 (pst_contest_vw)
                    vw_users = random.sample(users_list, min(vw_cnt, len(users_list)))
                    for v_i, v_user in enumerate(vw_users):
                        v_dt = base_dt + timedelta(minutes=v_i * 3)
                        cur.execute("""
                            INSERT IGNORE INTO pst_contest_vw (CONTEST_ROUND, ROUND_NO, VW_USER_ID, VW_DT)
                            VALUES (%s, %s, %s, %s)
                        """, (c_round, round_no, v_user[0], v_dt))

                    # 하위 좋아요 레코드 (pst_contest_like)
                    like_users = random.sample(users_list, min(like_cnt, len(users_list)))
                    for l_i, l_user in enumerate(like_users):
                        l_dt = base_dt + timedelta(minutes=l_i * 7 + 2)
                        cur.execute("""
                            INSERT IGNORE INTO pst_contest_like (CONTEST_ROUND, ROUND_NO, LIKE_USER_ID, LIKE_DT)
                            VALUES (%s, %s, %s, %s)
                        """, (c_round, round_no, l_user[0], l_dt))

                    # 하위 댓글 레코드 (pst_contest_cmt)
                    cmt_users = random.sample(users_list, min(cmt_cnt, len(users_list)))
                    for c_i, c_user in enumerate(cmt_users):
                        c_text = random.choice(sample_comments)
                        c_dt = base_dt + timedelta(minutes=c_i * 15 + 5)
                        cur.execute("""
                            INSERT IGNORE INTO pst_contest_cmt (CONTEST_ROUND, ROUND_NO, CMT_USER_ID, CMT, CMD_DT)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (c_round, round_no, c_user[0], c_text, c_dt))

                    total_posts_created += 1

                print(f"  └ 회차 #{c_round} 포스트 20개 및 관련 좋아요/댓글/조회수 시딩 완료!")

            # 7. 지난 회차(회차 1, 2)에 대해 명예의 전당 (pst_contest_award) 및 순위 집계 자동 부여
            print("\n🏆 지난 회차 (제1회, 제2회) 명예의 전당 수상작(pst_contest_award) 자동 집계 생성...")
            for c_round in [1, 2]:
                # 전체 순위 정렬
                cur.execute("""
                    SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                    FROM pst_contest_round
                    WHERE CONTEST_ROUND = %s
                    ORDER BY SCORE DESC, CMT_CNT DESC, LIKE_CNT DESC, VW_CNT DESC
                """, (c_round,))
                ranked_posts = cur.fetchall()

                # 1) 전체 1, 2, 3위 (AWARD_PART: 'G002P001')
                award_types = [('P001A101', 1), ('P001A102', 2), ('P001A103', 3)]
                for award_cd, rk in award_types:
                    if len(ranked_posts) >= rk:
                        winner = ranked_posts[rk - 1]
                        cur.execute("""
                            INSERT INTO pst_contest_award (CONTEST_ROUND, AWARD_PART, AWARD_CD, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                            VALUES (%s, 'G002P001', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (c_round, award_cd, winner['ROUND_NO'], winner['ENT_USER_ID'], winner['KIND_CD'], winner['VW_CNT'], winner['LIKE_CNT'], winner['CMT_CNT'], winner['SCORE'], rk))
                        
                        # total ranking update
                        cur.execute("""
                            UPDATE pst_contest_round SET TOTAL_RANKING = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                        """, (rk, c_round, winner['ROUND_NO']))

                # 2) 품종별 1, 2, 3위 (AWARD_PART: 'G002P002')
                cur.execute("""
                    SELECT DISTINCT KIND_CD FROM pst_contest_round WHERE CONTEST_ROUND = %s
                """, (c_round,))
                kinds = cur.fetchall()

                for k_item in kinds:
                    k_code = k_item['KIND_CD']
                    cur.execute("""
                        SELECT CONTEST_ROUND, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE
                        FROM pst_contest_round
                        WHERE CONTEST_ROUND = %s AND KIND_CD = %s
                        ORDER BY SCORE DESC, CMT_CNT DESC, LIKE_CNT DESC, VW_CNT DESC
                    """, (c_round, k_code))
                    k_ranked = cur.fetchall()

                    f_awards = [('P002A901', 1), ('P002A902', 2), ('P002A903', 3)]
                    for award_cd, rk in f_awards:
                        if len(k_ranked) >= rk:
                            k_winner = k_ranked[rk - 1]
                            cur.execute("""
                                INSERT INTO pst_contest_award (CONTEST_ROUND, AWARD_PART, AWARD_CD, ROUND_NO, ENT_USER_ID, KIND_CD, VW_CNT, LIKE_CNT, CMT_CNT, SCORE, RANKING)
                                VALUES (%s, 'G002P002', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (c_round, award_cd, k_winner['ROUND_NO'], k_winner['ENT_USER_ID'], k_winner['KIND_CD'], k_winner['VW_CNT'], k_winner['LIKE_CNT'], k_winner['CMT_CNT'], k_winner['SCORE'], rk))

                            # kind ranking update
                            cur.execute("""
                                UPDATE pst_contest_round SET KIND_RANKING = %s WHERE CONTEST_ROUND = %s AND ROUND_NO = %s
                            """, (rk, c_round, k_winner['ROUND_NO']))

            conn.commit()
            print("\n" + "=" * 65)
            print(f"🎉 성공적으로 지난 회차 2개 및 진행 중 회차 1개의 모든 데이터 시딩이 완수되었습니다!")
            print(f"   - 생성된 포스트 총 {total_posts_created}개")
            print(f"   - 사용된 이미지: {len(image_files)}개 (/static/sample_image/sample_01.jpg ~ sample_20.jpg)")
            print("=" * 65)

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ 시딩 중 오류 발생:", e)
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_seed()
