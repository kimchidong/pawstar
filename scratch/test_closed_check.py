from services.contest_service import PawStarService

def test_closed_check():
    service = PawStarService()
    conn = service.get_db_connection()
    if not conn:
        print("DB Connection Error")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT c.CONTEST_ROUND, c.CONTEST_STAT FROM pst_contest c LIMIT 5;")
        rows = cur.fetchall()
        print("Contest Rows in DB:", rows)

        for r in rows:
            c_round = r['CONTEST_ROUND']
            is_closed = service.is_contest_closed(c_round)
            post = service.get_post_detail(c_round, 1)
            print(f"Round {c_round}: DB STAT={r['CONTEST_STAT']}, is_closed={is_closed}")
            if post:
                print(f" -> Post post['is_closed']={post.get('is_closed')}, post['closed']={post.get('closed')}")

    conn.close()
    print("Closed status check complete!")

if __name__ == '__main__':
    test_closed_check()
