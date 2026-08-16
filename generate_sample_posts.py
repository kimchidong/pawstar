# -*- coding: utf-8 -*-
"""
Paw Star 샘플 게시물 자동 생성 배치 스크립트 (generate_sample_posts.py)
/static/sample_image 폴더의 펫 이미지들을 읽어 데이터베이스 POST 테이블에 풍성한 샘플 출전 포스트를 자동 생성합니다.
"""

import os
import sys
import io
import random
import pymysql
from datetime import datetime, timedelta
import importlib
try:
    config_web = importlib.import_module("config.web")
    DB_CONFIG = config_web.DB_CONFIG
except Exception:
    from config.web import DB_CONFIG

# Windows 콘솔 인코딩 대응
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_samples():
    print("=" * 60)
    print("🐾 Paw Star - 샘플 게시물 데이터 자동 생성기")
    print("=" * 60)

    # 1. 샘플 이미지 디렉터리 확인
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_img_dir = os.path.join(base_dir, 'static', 'sample_image')
    
    # 만약 절대 경로 D:\dev\pawstar\sample_image 존재 시 우선 참조
    alt_dir = r"D:\dev\pawstar\sample_image"
    if os.path.exists(alt_dir) and os.listdir(alt_dir):
        sample_img_dir = alt_dir

    if not os.path.exists(sample_img_dir):
        print(f"❌ 샘플 이미지 디렉터리를 찾을 수 없습니다: {sample_img_dir}")
        return

    # 이미지 파일 목록 수집
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    image_files = [f for f in os.listdir(sample_img_dir) if f.lower().endswith(valid_exts)]
    image_files.sort()

    if not image_files:
        print(f"❌ '{sample_img_dir}' 폴더에 이미지 파일이 없습니다.")
        return

    print(f"📸 발견된 샘플 이미지 개수: {len(image_files)}개")

    # 2. 메타 샘플 데이터 데이터셋 정의
    sample_metadata = [
        {"name": "뽀삐", "type": "🐕 강아지", "title": "햇살 가득 머금은 웃는 모습 ☀️", "content": "오늘 산책하면서 찍은 인생샷입니다! 카메라만 대면 이렇게 예쁘게 웃어줘요 🐶❤️"},
        {"name": "나비", "type": "🐈 고양이", "title": "식빵 굽는 보송보송 찹쌀떡 🍞", "content": "골골송 부르며 골골 대는 모습이 너무 사랑스러워요~ 집사 심장 심쿵 폭발 중!"},
        {"name": "모찌", "type": "🐹 햄스터", "title": "해바라기씨 볼빵빵 탐식가 🌻", "content": "볼주머니 가득 해바라기씨 넣고 뽈뽈거리는 우리 모찌 자랑해봅니다 🐹✨"},
        {"name": "앵두", "type": "🦜 앵무새", "title": "노래하는 알록달록 무지개 깃털 🌈", "content": "아침마다 안녕~ 하고 인사해주는 미모의 앵무새 앵두예요 🦜🎵"},
        {"name": "몽이", "type": "🐕 강아지", "title": "복실복실 몽몽이의 솜사탕 매력 ☁️", "content": "미용하고 와서 보송보송함 그 자체입니다. 길 가던 분들이 다 구경했어요!"},
        {"name": "루이", "type": "🐈 고양이", "title": "에메랄드빛 눈동자의 캣초딩 💎", "content": "창밖 구경에 푹 빠진 루이입니다. 옆태 라인이 예술이지 않나요?"},
        {"name": "초코", "type": "🐕 강아지", "title": "장난감 인형 품에 꼭 안고 숙면 중 🧸", "content": "최애 애착 인형을 끌어안고 단잠에 빠진 우리 초코! 보는 내내 힐링됩니다."},
        {"name": "두부", "type": "🐕 강아지", "title": "말랑말랑 말티즈 뭉클 귀요미 🤍", "content": "간식 소리만 들으면 귀가 쫑긋해지는 두부의 심쿵 눈빛 발사!"},
        {"name": "호두", "type": "🐹 햄스터", "title": "챗바퀴 달리기 챔피언 호두 🏃‍♂️", "content": "오늘도 멈추지 않는 호두의 운동 열정! 건강하게 오래오래 함께하자~"},
        {"name": "망고", "type": "🐈 고양이", "title": "노란 털 뭉치 햇살 낮잠 타이밍 🍊", "content": "따스한 햇살 아래서 나른하게 졸고 있는 오렌지빛 망고의 애교 넘치는 하루."},
        {"name": "코코", "type": "🐕 강아지", "title": "산책 나가기 전 무한 꼬리 펠러 🚁", "content": "리드줄만 들면 신나서 헬리콥터처럼 꼬리를 흔드는 귀염둥이 코코입니다!"},
        {"name": "치즈", "type": "🐈 고양이", "title": "상자 속 쏙 들어간 식빵 치즈 🧀", "content": "아무리 작은 택배 상자라도 자기 몸을 구겨 넣는 신기한 우리 집냥이 치즈."},
        {"name": "구름", "type": "🐕 강아지", "title": "폭신폭신 구름이의 하트 눈빛 ☁️", "content": "퇴근하고 집에 오면 제일 먼저 반겨주는 내 사랑 구름이의 멍뭉미!"},
        {"name": "까미", "type": "🐈 고양이", "title": "까만 보석 눈동자의 카리스마 🖤", "content": "어둠 속에서도 빛나는 까미의 미모! 집사바라기 카리스마 냥이입니다."},
        {"name": "초롱", "type": "🐕 강아지", "title": "눈망울 초롱초롱 힐링 귀요미 ✨", "content": "간식 하나 얻어먹으려고 세상에서 가장 아련한 표정을 짓는 초롱이에요."},
        {"name": "바다", "type": "🦜 앵무새", "title": "파란 깃털 날리며 웰컴 인사 🌊", "content": "손가락 위로 살포시 올라와 깃털 다듬는 예쁜 바다의 평화로운 일상!"},
        {"name": "콩이", "type": "🐕 강아지", "title": "귀염뽀짝 앙증맞은 발바닥 젤리 🐾", "content": "꼬소한 꼬랑내 나는 핑크 발바닥 젤리가 매력 포인트인 콩이입니다."},
        {"name": "레오", "type": "🐈 고양이", "title": "캣타워 정상에서 왕이 된 기분 👑", "content": "높은 곳에 올라가 집사를 내려다보며 사자처럼 당당한 레오의 도도함!"},
        {"name": "자몽", "type": "🐰 토끼", "title": "오물오물 당근 먹방 라이브 🥕", "content": "당근 조각을 옴뇸뇸 맛있게 먹는 귀여운 토끼 자몽이의 씹덕 포인트!"},
        {"name": "보리", "type": "🐕 강아지", "title": "바람을 가르며 달리는 강아지 🌾", "content": "잔디밭을 신나게 달리며 스트레스 제로가 된 보리의 맑고 깨끗한 웃음!"}
    ]

    sample_comments = [
        "너무 사랑스럽네요! 투표 하트 꾹 누르고 갑니다 ❤️",
        "우와~ 인형 아닌가요? 심쿵사할 뻔했어요 🥺✨",
        "표정이 어쩜 이렇게 예쁘죠? 이번 콘테스트 우승 가자!",
        "눈동자가 정말 보석 같아요~ 응원합니다! 💎",
        "보는 내내 미소가 절로 나네요 ㅎㅎ 건강하게 잘 자라렴 🐾",
        "우리아이보다 더 귀여운 것 같아요! 완전 스타감이네요 👍",
        "힐링 제대로 하고 갑니다~ 1등 응원해요 👑"
    ]

    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            # 3. 현재 진행 중인 콘테스트 ID 조회
            cur.execute("SELECT CONTEST_ID FROM CONTEST WHERE STATUS = 'IN_PROGRESS' ORDER BY CONTEST_ID ASC LIMIT 1")
            row = cur.fetchone()
            contest_id = row['CONTEST_ID'] if row else 1

            # 4. 사용자 목록 조회
            cur.execute("SELECT USER_ID, NICKNAME FROM USERS")
            users = cur.fetchall()
            if not users:
                print("⚠️ 등록된 유저가 없어 기본 유저 ID를 사용합니다.")
                users = [{'USER_ID': 'user1', 'NICKNAME': '뽀삐아빠'}]

            inserted_count = 0
            for idx, img_name in enumerate(image_files):
                meta = sample_metadata[idx % len(sample_metadata)]
                user = users[idx % len(users)]
                user_id = user['USER_ID']

                pet_name = meta['name']
                pet_type = meta['type']
                title = meta['title']
                content = meta['content']
                file_path = f"/static/sample_image/{img_name}"

                # 수치 계산: 조회수 60~350, 좋아요 15~180, 댓글 2~15
                view_cnt = random.randint(60, 350)
                like_cnt = random.randint(15, 180)
                comment_cnt = random.randint(2, 15)
                
                # 점수 공식: (조회수 * 1) + (좋아요 * 5) + (댓글 * 10)
                score = (view_cnt * 1) + (like_cnt * 5) + (comment_cnt * 10)
                
                # 생성이력 시간 산출 (최근 1~10일 전 난수)
                created_dt = datetime.now() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))

                # POST INSERT
                cur.execute("""
                    INSERT INTO POST (CONTEST_ID, USER_ID, PET_NAME, PET_TYPE, TITLE, CONTENT, FILE_PATH, LIST_FILE_NAME, POPUP_FILE_NAME, SCORE, VIEW_COUNT, LIKE_COUNT, COMMENT_COUNT, CREATED_AT)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (contest_id, user_id, pet_name, pet_type, title, content, file_path, img_name, img_name, score, view_cnt, like_cnt, comment_cnt, created_dt))
                
                post_id = cur.lastrowid
                inserted_count += 1

                # 샘플 댓글 생성 (post_comment)
                num_comments = min(comment_cnt, random.randint(2, 5))
                for c_idx in range(num_comments):
                    c_user = users[(idx + c_idx + 1) % len(users)]
                    c_text = random.choice(sample_comments)
                    c_dt = created_dt + timedelta(minutes=random.randint(10, 120))
                    cur.execute("""
                        INSERT INTO post_comment (post_id, user_id, user_nickname, user_profile, content, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (post_id, c_user['USER_ID'], c_user['NICKNAME'], '/static/image/profile/default_profile.png', c_text, c_dt))

                print(f"  [{inserted_count}/{len(image_files)}] 🐾 '{pet_name}' ({pet_type}) | 제목: {title} | 점수: {score}P 생성 완료")

            conn.commit()
            print("=" * 60)
            print(f"🎉 총 {inserted_count}개의 고품질 샘플 포스트 생성이 성공적으로 완료되었습니다!")
            print("=" * 60)
    except Exception as e:
        conn.rollback()
        print(f"❌ 데이터 생성 중 오류 발생: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    generate_samples()
