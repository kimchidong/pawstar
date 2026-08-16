# -*- coding: utf-8 -*-
"""
PST_THEME 테이블 원복 스크립트 (restore_PST_THEME.py)
PST_THEME 테이블을 1월부터 12월까지의 정규 표준 12종 테마 데이터로 복원하고,
PST_CONTEST 회차들의 THEME_CD 외래키 연결을 정상 원복합니다.
"""

import sys
import io
import pymysql
import os
import importlib.util

def _get_config_web():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, 'config.web.py'),
        os.path.join(curr_dir, '..', 'config.web.py'),
        os.path.join(os.getcwd(), 'config.web.py')
    ]
    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("config_web", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("config.web.py 파일을 찾을 수 없습니다.")

config_web = _get_config_web()
DB_CONFIG = config_web.DB_CONFIG

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def restore_theme():
    print("==================================================")
    print("🐾 PST_THEME 테이블 및 회차 테마 데이터 원복 시작")
    print("==================================================")

    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    if not conn:
        print("❌ DB 연결 실패!")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # 1. PST_THEME 테이블 전체 초기화 및 12개 월별 표준 테마 재시딩
            cur.execute("TRUNCATE TABLE PST_THEME;")

            original_themes = [
                ('T001', 1, '새해 맞이', '복을 부르는 천사 같은 아이들의 건강하고 맑은 복덩이 순간 🌅', '/static/image/banner/T001.png'),
                ('T002', 2, '발렌타인 심쿵', '달콤한 초콜릿보다 훨씬 더 짜릿하고 러블리한 심쿵 포옹 🍫', '/static/image/banner/T002.png'),
                ('T003', 3, '봄맞이 설렘', '속삭이는 봄바람 타고 살랑살랑 피어나는 풋풋한 봄날 🌸', '/static/image/banner/T003.png'),
                ('T004', 4, '벚꽃 피크닉', '따스한 봄햇살 아래 무해한 미소로 심장을 어택하는 봄날의 천사들 ☀️', '/static/image/banner/T004.png'),
                ('T005', 5, '가정의 달 펫 패밀리', '온 집안을 환하게 밝혀주는 최고의 복덩이 펫 가족을 소개합니다 💖', '/static/image/banner/T005.png'),
                ('T006', 6, '청량 힐링', '싱그러운 푸른 유월, 활기찬 꼬리치기 속에 퍼지는 싱그러운 매력 🌿', '/static/image/banner/T006.png'),
                ('T007', 7, '썸머 파라다이스', '무더위를 날려버릴 사이다처럼 쿨하고 세련된 우리 아이 힐링 미소 🌊', '/static/image/banner/T007.png'),
                ('T008', 8, '한여름 밤의 바캉스', '파도 소리와 함께 즐기는 핫한 바캉스! 여름 최고의 슈퍼스타 등장 🌴', '/static/image/banner/T008.png'),
                ('T009', 9, '가을 풍요', '오색 단풍처럼 풍성하고 기품 넘치는 아늑한 가을날의 명작 퍼레이드 🍁', '/static/image/banner/T009.png'),
                ('T010', 10, '할로윈 펌킨', '간식을 안 주면 앙탈부릴 거야! 귀여운 악마들의 심쿵 할로윈 파티 🎃', '/static/image/banner/T010.png'),
                ('T011', 11, '단풍 낭만', '포근한 낙엽 카펫 위에서 나누는 정겨운 훈훈함, 늦가을의 힐링 펫 🍂', '/static/image/banner/T011.png'),
                ('T012', 12, '홀리데이 크리스마스', '하얀 눈처럼 순수한 우리 아이들과 함께하는 따스한 성탄절 기적 🎄', '/static/image/banner/T012.png')
            ]

            for t_cd, mnth, t_nm, t_ment, t_banner in original_themes:
                cur.execute("""
                    INSERT INTO PST_THEME (THEME_CD, MNTH, THEME_NM, THEME_MENT, BANNER_IMG_FILE_PATH)
                    VALUES (%s, %s, %s, %s, %s)
                """, (t_cd, mnth, t_nm, t_ment, t_banner))

            print("✅ PST_THEME 테이블 12종 정규 테마(T001~T012) 원복 완료!")

            # 2. PST_CONTEST 회차별 THEME_CD 연결 원복
            # 회차 1 -> T006 (6월 청량 힐링), 회차 2 -> T007 (7월 썸머 파라다이스), 회차 3 -> T008 (8월 한여름 밤의 바캉스)
            cur.execute("UPDATE PST_CONTEST SET THEME_CD = 'T006' WHERE CONTEST_ROUND = 1;")
            cur.execute("UPDATE PST_CONTEST SET THEME_CD = 'T007' WHERE CONTEST_ROUND = 2;")
            cur.execute("UPDATE PST_CONTEST SET THEME_CD = 'T008' WHERE CONTEST_ROUND = 3;")

            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()

            print("✅ PST_CONTEST 회차별 테마 연결 (회차 1: T006, 회차 2: T007, 회차 3: T008) 원복 완료!")
            print("==================================================")

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ 원복 처리 중 오류 발생:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    restore_theme()
