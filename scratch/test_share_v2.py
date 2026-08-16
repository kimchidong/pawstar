import pymysql
import uuid
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
from services.contest_service import PawStarService
from app import app

def test_all_requirements():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Error")
        return

    with conn.cursor() as cur:
        # 1. S- 접두어 생성 검증
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, SHARE_SN, SHARE_CNT, SCORE FROM pst_contest_round LIMIT 1;")
        post = cur.fetchone()
        assert post['SHARE_SN'] and post['SHARE_SN'].startswith('S-'), f"SHARE_SN must start with S-, got {post['SHARE_SN']}"
        print(f"1. SHARE_SN format test passed: {post['SHARE_SN']}")

        c_round = post['CONTEST_ROUND']
        r_no = post['ROUND_NO']
        s_sn = post['SHARE_SN']

        # 2. 전용 공유 랜딩 페이지 HTTP 200 OK 응답 검증
        client = app.test_client()
        res = client.get(f'/share?contest_round={c_round}&round_no={r_no}&share_sn={s_sn}')
        assert res.status_code == 200, f"Dedicated share page failed with status {res.status_code}"
        assert '전용 공유 추천 링크 유입' in res.get_data(as_text=True), "Share landing template content missing"
        print("2. Dedicated share landing page (/share) HTTP 200 OK test passed!")

        # 3. 모바일 전용 랜딩 페이지 HTTP 200 OK 응답 검증
        res_m = client.get(f'/m/share?contest_round={c_round}&round_no={r_no}&share_sn={s_sn}')
        assert res_m.status_code == 200, f"Mobile dedicated share page failed with status {res_m.status_code}"
        print("3. Mobile dedicated share landing page (/m/share) HTTP 200 OK test passed!")

        print("\nAll V2 requirements successfully verified!")

    conn.close()

if __name__ == '__main__':
    test_all_requirements()
