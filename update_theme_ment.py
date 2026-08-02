# -*- coding: utf-8 -*-
"""
PST_THEME 테이블 THEME_NM 및 THEME_MENT 컬럼 업데이트 스크립트 (update_theme_ment.py)
각 월별 계절감과 축제 특성에 딱 들어맞는 감성적인 테마 명칭(THEME_NM)과 소개 멘트(THEME_MENT)를 갱신합니다.
"""

import sys
import io
import pymysql
from config import db_config

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def update_theme_ment():
    print("==================================================")
    print("🐾 PST_THEME 월별 THEME_NM & THEME_MENT 업데이트 시작")
    print("==================================================")

    monthly_themes = [
        {
            "code": "T001",
            "name": "새해 맞이 펫스타 콘테스트 🌅",
            "ment": "새해 복 많이 받으세요! 희망찬 새해 첫 태양 아래 맑은 미소로 찾아온 최고 복덩이 펫 스타 🌅✨"
        },
        {
            "code": "T002",
            "name": "발렌타인 심쿵 펫 챔피언십 🍫",
            "ment": "달콤한 초콜릿보다 훨씬 더 사랑스럽고 심쿵사 유발하는 세상 제일 러블리한 펫 순간 🍫❤️"
        },
        {
            "code": "T003",
            "name": "봄맞이 설렘 펫 콘테스트 🌸",
            "ment": "속삭이는 봄바람 따라 살랑살랑 피어나는 풋풋하고 따스한 봄날의 댕냥이 자랑 🌸🐝"
        },
        {
            "code": "T004",
            "name": "벚꽃 피크닉 펫 챔피언십 🌸🐕",
            "ment": "화사한 벚꽃 잎 날리는 봄날 피크닉! 햇살 아래 무해한 미소로 심장을 사르르 녹이는 아이들 ☀️🌿"
        },
        {
            "code": "T005",
            "name": "가정의 달 펫 패밀리 콘테스트 🏡💖",
            "ment": "우리 집 보물 1호! 온 집안을 환하게 밝혀주는 세상에서 가장 따뜻한 펫 가족의 순간 🏡💖"
        },
        {
            "code": "T006",
            "name": "청량 힐링 초여름 펫스타 🌿🌊",
            "ment": "싱그러운 유월의 푸르름! 보기만 해도 더위가 싹 가시는 맑고 청량한 힐링 펫 스타 🌿🌊"
        },
        {
            "code": "T007",
            "name": "썸머 파라다이스 펫 콘테스트 🏖️🍦",
            "ment": "무더위를 싹 씻어줄 사이다처럼 쿨하고 시원 세련된 여름 파라다이스 최고 인플루언서 펫 🏖️🍦"
        },
        {
            "code": "T008",
            "name": "한여름 밤의 바캉스 펫 챔피언십 🌴⭐",
            "ment": "시원한 파도 소리와 함께 즐기는 핫 바캉스! 여름밤을 뜨겁게 밝히는 펫 챔피언전 🌴⭐"
        },
        {
            "code": "T009",
            "name": "가을 풍요 한가위 펫 콘테스트 🌾🍁",
            "ment": "풍성한 한가위 둥글둥글 마음까지 풍요로워지는 아늑하고 기품 넘치는 가을 펫 스타 🌾🍁"
        },
        {
            "code": "T010",
            "name": "할로윈 펌킨 펫 파티 🎃👻",
            "ment": "간식을 안 주면 앙탈부릴 거야! 심장 멎는 큐트 깜찍이들의 할로윈 코스튬 파티 🎃👻"
        },
        {
            "code": "T011",
            "name": "단풍 낭만 펫 콘테스트 🍁☕",
            "ment": "바스락 단풍 낙엽길 따라 찾아온 정겨움과 훈훈함, 감성 만점 늦가을 힐링 펫 라이프 🍁☕"
        },
        {
            "code": "T012",
            "name": "홀리데이 크리스마스 펫스타 🎄🎁",
            "ment": "메리 크리스마스! 산타 옷 입고 하얀 눈처럼 순수한 우리 아이들이 선물하는 성탄절 기적 🎄🎁"
        }
    ]

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    if not conn:
        print("❌ DB 연결 실패!")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SET NAMES utf8mb4;")
            for theme in monthly_themes:
                cur.execute("""
                    UPDATE pst_theme
                    SET THEME_NM = %s, THEME_MENT = %s
                    WHERE THEME_CD = %s
                """, (theme["name"], theme["ment"], theme["code"]))
                print(f"  [{theme['code']}] {theme['name']} -> 업데이트 완료")

            conn.commit()
            print("\n==================================================")
            print("🎉 모든 12개 월별 THEME_NM & THEME_MENT 업데이트 완료!")
            print("==================================================")
    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ 업데이트 실패:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_theme_ment()
