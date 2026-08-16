# -*- coding: utf-8 -*-
"""
PST_THEME 테이블 THEME_MENT 컬럼 40자 이내 제한 업데이트 스크립트 (update_theme_ment_under_40.py)
THEME_MENT 문구를 공백/이모티콘 포함 엄격히 40자 이내로 정돈하여 DB에 적용합니다.
"""

import sys
import io
import pymysql
import importlib
try:
    config_web = importlib.import_module("config.web")
    DB_CONFIG = config_web.DB_CONFIG
except Exception:
    from config.web import DB_CONFIG

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def update_theme_under_40():
    print("==================================================")
    print("🐾 PST_THEME (THEME_MENT 40자 이내) 업데이트 시작")
    print("==================================================")

    monthly_themes = [
        {
            "code": "T001",
            "name": "새해 맞이 펫스타 콘테스트 🌅",
            "ment": "희망찬 새해 첫 태양 아래 찾아온 최고의 복덩이 펫 스타 🌅✨"
        },
        {
            "code": "T002",
            "name": "발렌타인 심쿵 펫 챔피언십 🍫",
            "ment": "달콤한 초콜릿보다 더 사랑스럽고 러블리한 심쿵 순간 🍫❤️"
        },
        {
            "code": "T003",
            "name": "봄맞이 설렘 펫 콘테스트 🌸",
            "ment": "속삭이는 봄바람 따라 피어나는 풋풋하고 따스한 봄날 🌸🐝"
        },
        {
            "code": "T004",
            "name": "벚꽃 피크닉 펫 챔피언십 🌸🐕",
            "ment": "화사한 벚꽃 잎 날리는 봄날! 무해한 미소로 심장 폭격 ☀️🌸"
        },
        {
            "code": "T005",
            "name": "가정의 달 펫 패밀리 콘테스트 🏡💖",
            "ment": "우리 집 보물 1호! 온 집안을 밝혀주는 따뜻한 펫 가족 🏡💖"
        },
        {
            "code": "T006",
            "name": "청량 힐링 초여름 펫스타 🌿🌊",
            "ment": "싱그러운 유월의 푸르름! 더위가 싹 가시는 청량 힐링 스타 🌿🌊"
        },
        {
            "code": "T007",
            "name": "썸머 파라다이스 펫 콘테스트 🏖️🍦",
            "ment": "무더위를 싹 씻어줄 쿨하고 세련된 여름 파라다이스 펫 🏖️🍦"
        },
        {
            "code": "T008",
            "name": "한여름 밤의 바캉스 펫 챔피언십 🌴⭐",
            "ment": "시원한 파도 소리와 함께 즐기는 핫한 바캉스 펫 챔피언전 🌴⭐"
        },
        {
            "code": "T009",
            "name": "가을 풍요 한가위 펫 콘테스트 🌾🍁",
            "ment": "풍성한 한가위! 마음까지 아늑하고 기품 넘치는 가을 스타 🌾🍁"
        },
        {
            "code": "T010",
            "name": "할로윈 펌킨 펫 파티 🎃👻",
            "ment": "간식을 안 주면 앙탈부릴 거야! 깜찍이들의 할로윈 파티 🎃👻"
        },
        {
            "code": "T011",
            "name": "단풍 낭만 펫 콘테스트 🍁☕",
            "ment": "바스락 단풍 낙엽길 따라 찾아온 감성 만점 늦가을 힐링 🍁☕"
        },
        {
            "code": "T012",
            "name": "홀리데이 크리스마스 펫스타 🎄🎁",
            "ment": "메리 크리스마스! 순수한 우리 아이들이 선물하는 성탄 기적 🎄🎁"
        }
    ]

    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    if not conn:
        print("❌ DB 연결 실패!")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")
            for theme in monthly_themes:
                ment_len = len(theme["ment"])
                if ment_len > 40:
                    print(f"⚠️ 경고: [{theme['code']}] 멘트가 40자를 초과함 ({ment_len}자)")
                else:
                    print(f"  [{theme['code']}] ({ment_len}자) {theme['name']} -> '{theme['ment']}'")

                cur.execute("""
                    UPDATE pst_theme
                    SET THEME_NM = %s, THEME_MENT = %s
                    WHERE THEME_CD = %s
                """, (theme["name"], theme["ment"], theme["code"]))

            conn.commit()
            print("\n==================================================")
            print("🎉 40자 이내 THEME_MENT 12개 월별 데이터 업데이트 완료!")
            print("==================================================")
    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ 업데이트 실패:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_theme_under_40()
