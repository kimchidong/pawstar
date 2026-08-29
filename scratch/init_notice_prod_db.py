import pymysql
from datetime import datetime
import os
import sys

# 서비스 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.contest_service import service

def sync_prod_notice_tables():
    conn = service.get_db_connection()
    if not conn:
        print("DB 커넥션 실패")
        return

    try:
        with conn.cursor() as cur:
            # 대문자 및 소문자 테이블 목록
            target_tables = ['PST_NOTICE', 'pst_notice']
            
            title_pc = '🎉 <strong style="color: #4338ca;">Paw Star 정식 오픈!</strong> 반려동물도 스타가 될 수 있다! 소중한 아이의 특별한 순간을 공유하고 펫 스타에 도전해 보세요! 🌟'
            title_m = '🎉 <strong style="color: #4338ca;">Paw Star 정식 오픈!</strong> 소중한 아이의 사랑스러운 순간을 공유하고 펫 스타에 도전해보세요! 🌟'

            content_pc = """
<div class="notice-detail-content">
    <div class="notice-poster-wrap" style="margin-bottom: 1.75rem; text-align: center;">
        <img src="/static/image/poster/notice_open_poster.jpg?v=20260901_1" alt="Paw Star 정식 오픈 포스터" style="width: 100%; max-width: 860px; height: auto; border-radius: 16px; box-shadow: 0 4px 20px rgba(124, 58, 237, 0.15); border: 1px solid #e2e8f0; display: block; margin: 0 auto;">
    </div>

    <div class="notice-highlight-box">
        <h3 class="notice-highlight-title">
            <i class="fa-solid fa-crown"></i>
            <span>반려동물도 스타가 될 수 있다!</span>
        </h3>
        <p class="notice-highlight-desc">
            Paw Star는 세상에 하나뿐인 나의 소중한 반려동물을 마음껏 자랑하고, 매월 투표를 통해 명예의 전당 펫 스타로 선정되는 프리미엄 반려동물 콘테스트 플랫폼입니다.
        </p>
    </div>

    <div class="notice-section">
        <h3 class="notice-section-title">
            <i class="fa-solid fa-sparkles"></i>
            <span>Paw Star 주요 이용 안내</span>
        </h3>
        
        <div class="notice-grid-3">
            <div class="notice-card-item">
                <div class="card-icon violet"><i class="fa-solid fa-camera"></i></div>
                <h4 class="card-title">01. 출전하기</h4>
                <p class="card-desc">소중한 반려동물의 러블리한 일상 사진 및 SNS 링크(인스타/유튜브 등)로 출전해 보세요.</p>
            </div>

            <div class="notice-card-item">
                <div class="card-icon pink"><i class="fa-solid fa-heart"></i></div>
                <h4 class="card-title">02. 응원과 투표</h4>
                <p class="card-desc">마음에 드는 아이에게 하트를 보내고 댓글로 따뜻하게 응원해 보세요.</p>
            </div>

            <div class="notice-card-item">
                <div class="card-icon amber"><i class="fa-solid fa-trophy"></i></div>
                <h4 class="card-title">03. 명예의 전당</h4>
                <p class="card-desc">매월 상위 랭킹을 달성한 펫 스타들은 명예의 전당에 등재됩니다.</p>
            </div>
        </div>
    </div>
</div>
"""

            content_m = """
<div class="notice-detail-content">
    <div class="m-notice-poster-wrap" style="margin-bottom: 0.85rem; text-align: center;">
        <img src="/static/image/poster/notice_open_poster.jpg?v=20260901_1" alt="Paw Star 정식 오픈 포스터" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 3px 12px rgba(124, 58, 237, 0.12); border: 1px solid #e2e8f0; display: block;">
    </div>
    <div class="notice-highlight-box" style="background: linear-gradient(135deg, #f5f3ff 0%, #fce7f3 100%); border: 1.5px solid #e9d5ff; border-left: 5px solid #7c3aed; border-radius: 14px; padding: 0.75rem 0.85rem; margin-bottom: 0.85rem;">
        <h4 class="notice-highlight-title" style="color: #7c3aed; font-size: 0.82rem; font-weight: 900; margin: 0 0 0.25rem 0; display: flex; align-items: center; gap: 0.35rem;">
            <i class="fa-solid fa-crown" style="color: #eab308; font-size: 0.8rem;"></i>
            <span>반려동물도 스타가 될 수 있다!</span>
        </h4>
        <p class="notice-highlight-desc" style="color: #581c87; font-size: 0.72rem; line-height: 1.4; margin: 0; font-weight: 600;">
            Paw Star는 우리 집 소중한 아이를 자랑하고, 매월 투표를 통해 펫 스타로 등극하는 반려동물 대표 콘테스트 공간입니다. 🐾
        </p>
    </div>

    <div class="notice-section" style="margin-bottom: 0.85rem;">
        <h4 class="notice-section-title" style="font-size: 0.82rem; font-weight: 900; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 0.35rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 0.35rem;">
            <i class="fa-solid fa-paw" style="color: #7c3aed; font-size: 0.8rem;"></i>
            <span>Paw Star 200% 즐기는 방법</span>
        </h4>
        
        <div class="m-notice-card-wrap">
            <div class="m-notice-step-card purple">
                <div class="m-step-badge purple"><i class="fa-solid fa-camera"></i></div>
                <div class="m-step-info">
                    <span class="m-step-num purple">STEP 01</span>
                    <span class="m-step-title">출전하기</span>
                    <span class="m-step-desc">사랑스러운 아이 사진 & SNS 링크로 바로 출전!</span>
                </div>
            </div>

            <div class="m-notice-step-card pink">
                <div class="m-step-badge pink"><i class="fa-solid fa-heart"></i></div>
                <div class="m-step-info">
                    <span class="m-step-num pink">STEP 02</span>
                    <span class="m-step-title">응원과 투표</span>
                    <span class="m-step-desc">원하는 출전작에 하트 투표하고 응원 메시지 남기기</span>
                </div>
            </div>

            <div class="m-notice-step-card amber">
                <div class="m-step-badge amber"><i class="fa-solid fa-trophy"></i></div>
                <div class="m-step-info">
                    <span class="m-step-num amber">STEP 03</span>
                    <span class="m-step-title">명예의 전당</span>
                    <span class="m-step-desc">매월 랭킹 상위 달성 펫 스타의 영예 등재!</span>
                </div>
            </div>
        </div>
    </div>
</div>
"""
            reg_dt = "2026-09-01 00:00:00"

            for tbl in target_tables:
                print(f"[{tbl}] 테이블 준비 및 데이터 동기화를 시작합니다...")
                create_sql = f"""
                CREATE TABLE IF NOT EXISTS `{tbl}` (
                    `NOTICE_NO` int NOT NULL AUTO_INCREMENT,
                    `TTL` varchar(250) DEFAULT NULL,
                    `TTL_M` varchar(250) NOT NULL,
                    `CONT` text DEFAULT NULL,
                    `CONT_M` text NOT NULL,
                    `REG_DT` datetime NOT NULL,
                    `MODE_DT` datetime NOT NULL,
                    PRIMARY KEY (`NOTICE_NO`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
                cur.execute(create_sql)
                conn.commit()

                cur.execute(f"SELECT COUNT(*) AS cnt FROM `{tbl}`")
                row = cur.fetchone()
                cnt = row['cnt'] if row else 0

                if cnt == 0:
                    insert_sql = f"""
                    INSERT INTO `{tbl}` (TTL, TTL_M, CONT, CONT_M, REG_DT, MODE_DT)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    cur.execute(insert_sql, (title_pc, title_m, content_pc, content_m, reg_dt, reg_dt))
                    conn.commit()
                    print(f" -> [{tbl}] 신규 데이터 INSERT 완료!")
                else:
                    update_sql = f"""
                    UPDATE `{tbl}`
                    SET TTL = %s, TTL_M = %s, CONT = %s, CONT_M = %s, REG_DT = %s, MODE_DT = %s
                    WHERE NOTICE_NO = 1;
                    """
                    cur.execute(update_sql, (title_pc, title_m, content_pc, content_m, reg_dt, reg_dt))
                    conn.commit()
                    print(f" -> [{tbl}] 기존 데이터 (NOTICE_NO=1) UPDATE 완료!")

    except Exception as e:
        print("[ERROR] 운영 테이블 처리 중 예외 발생:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    sync_prod_notice_tables()
