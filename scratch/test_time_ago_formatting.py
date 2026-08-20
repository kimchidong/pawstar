import os
import sys
import unittest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, time_ago_filter

class TestTimeAgoFormatting(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_python_time_ago_filter(self):
        now = datetime.datetime.now()

        # 1. 방금 전 (< 10s)
        dt_just_now = now - datetime.timedelta(seconds=3)
        self.assertEqual(time_ago_filter(dt_just_now.strftime('%Y-%m-%d %H:%M:%S')), '방금 전')

        # 2. 초 전 (10s ~ 59s)
        dt_sec = now - datetime.timedelta(seconds=25)
        self.assertEqual(time_ago_filter(dt_sec.strftime('%Y-%m-%d %H:%M:%S')), '25초 전')

        # 3. 분 전 (1m ~ 59m)
        dt_min = now - datetime.timedelta(minutes=14)
        self.assertEqual(time_ago_filter(dt_min.strftime('%Y-%m-%d %H:%M:%S')), '14분 전')

        # 4. 시간 전 (1h ~ 23h)
        dt_hour = now - datetime.timedelta(hours=5)
        self.assertEqual(time_ago_filter(dt_hour.strftime('%Y-%m-%d %H:%M:%S')), '5시간 전')

        # 5. 일 전 (1d ~ 29d)
        dt_day = now - datetime.timedelta(days=3)
        self.assertEqual(time_ago_filter(dt_day.strftime('%Y-%m-%d %H:%M:%S')), '3일 전')

        # 6. 달 전 (30d ~ 364d)
        dt_month = now - datetime.timedelta(days=65)
        self.assertEqual(time_ago_filter(dt_month.strftime('%Y-%m-%d %H:%M:%S')), '2달 전')

        # 7. 년 전 (>= 365d)
        dt_year = now - datetime.timedelta(days=400)
        self.assertEqual(time_ago_filter(dt_year.strftime('%Y-%m-%d %H:%M:%S')), '1년 전')

    def test_js_files_contain_format_time_ago(self):
        main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'main.js')
        with open(main_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function formatTimeAgo(', content)
        self.assertIn('return `${diffMonth}달 전`;', content)

        m_main_js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'm_main.js')
        with open(m_main_js_path, 'r', encoding='utf-8') as f:
            m_content = f.read()
        self.assertIn('function formatTimeAgo(', m_content)
        self.assertIn('return `${diffMonth}달 전`;', m_content)

if __name__ == '__main__':
    unittest.main()
