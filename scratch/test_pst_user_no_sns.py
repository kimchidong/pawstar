import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from services.contest_service import PawStarService

def test_no_pst_user_sns():
    service = PawStarService()
    conn = service.get_db_connection()
    assert conn is not None

    print("1) Testing get_user_profile query without PST_USER SNS columns...")
    res = service.get_user_profile('integration_test_user_777')
    print("get_user_profile result status:", bool(res))
    assert res is not None

    print("2) Testing update_user_profile without PST_USER SNS columns...")
    success, msg, u_obj = service.update_user_profile('integration_test_user_777', nickname='테스트집사777')
    print("update_user_profile result:", success, msg)
    assert success == True

    print("3) Testing get_posts (feed posts) query...")
    posts = service.get_posts(13)
    print(f"Fetched posts count for contest 13:", len(posts.get('posts', [])))

    print("4) Testing get_hall_of_fame query...")
    fame = service.get_hall_of_fame()
    print("Hall of fame items count:", len(fame))

    print("ALL PST_USER WITHOUT SNS COLUMNS TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_no_pst_user_sns()
