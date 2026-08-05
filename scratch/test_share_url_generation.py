from app import app
from services.contest_service import PawStarService

def test_share_url_api():
    client = app.test_client()
    service = PawStarService()
    
    # DB에서 존재하는 첫번째 콘테스트 게시물 라운드 정보 확인
    conn = service.get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT CONTEST_ROUND, ROUND_NO, SHARE_SN FROM pst_contest_round LIMIT 1;")
        row = cur.fetchone()
        c_round = row['CONTEST_ROUND']
        r_no = row['ROUND_NO']
    conn.close()

    # GET 요청 검증
    res_get = client.get(f'/api/contest/share_url?contest_round={c_round}&round_no={r_no}')
    assert res_get.status_code == 200, f"share_url API GET failed: {res_get.status_code}"
    data_get = res_get.get_json()
    assert data_get.get('success') is True, "success must be True"
    assert 'share_url' in data_get, "share_url field missing"
    
    share_url = data_get['share_url']
    print("Generated Share URL:", share_url)
    assert f"contest_round={c_round}" in share_url, f"contest_round missing in {share_url}"
    assert f"round_no={r_no}" in share_url, f"round_no missing in {share_url}"
    assert "share_sn=" in share_url, f"share_sn missing in {share_url}"

    print("\nShare URL Generation API test passed 100% successfully!")

if __name__ == '__main__':
    test_share_url_api()
