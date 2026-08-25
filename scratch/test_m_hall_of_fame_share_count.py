import importlib.util
import unittest

class TestHallOfFameShareCount(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('config_web', 'config.web.py')
        config_web = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_web)
        from services.contest_service import service
        self.service = service

    def test_hall_of_fame_share_count_present(self):
        winners = self.service.get_hall_of_fame(1)
        self.assertTrue(len(winners) > 0, "Winners list should not be empty")
        for winner in winners:
            self.assertIn('SHARE_CNT', winner, "SHARE_CNT should be in winner dict")
            self.assertIn('share_count', winner, "share_count should be in winner dict")
            self.assertIsNotNone(winner['SHARE_CNT'], "SHARE_CNT should not be None")
            self.assertIsNotNone(winner['share_count'], "share_count should not be None")
            print(f"Winner post_id: {winner.get('post_id')}, SHARE_CNT: {winner.get('SHARE_CNT')}, share_count: {winner.get('share_count')}")

if __name__ == '__main__':
    unittest.main()
