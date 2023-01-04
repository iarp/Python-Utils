import unittest

from iarp_utils.datetimes import weekday


class DatetimesWeekdayTests(unittest.TestCase):

    def test_full_day_name(self):
        self.assertEqual(0, weekday('sunday'))
        self.assertEqual(1, weekday('monday'))
        self.assertEqual(2, weekday('tuesday'))
        self.assertEqual(3, weekday('wednesday'))
        self.assertEqual(4, weekday('thursday'))
        self.assertEqual(5, weekday('friday'))
        self.assertEqual(6, weekday('saturday'))

    def test_short_day_name(self):
        self.assertEqual(0, weekday('sun'))
        self.assertEqual(1, weekday('mon'))
        self.assertEqual(2, weekday('tue'))
        self.assertEqual(3, weekday('wed'))
        self.assertEqual(4, weekday('thu'))
        self.assertEqual(5, weekday('fri'))
        self.assertEqual(6, weekday('sat'))
