import datetime
import unittest

from iarp_utils.datetimes import weekday, iterate_steps_between_datetimes


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

class DatetimeLoopIteratorTests(unittest.TestCase):
    def test_iterator_five_minutes(self):

        start = datetime.datetime(2022, 1, 4, 23, 0, 0)
        end = datetime.datetime(2022, 1, 5, 1, 30, 0)
        delta = datetime.timedelta(minutes=5)

        expected = []

        expected_start = start

        while expected_start <= end:
            expected.append(expected_start)
            expected_start += delta

        for dt in iterate_steps_between_datetimes(start, end, delta):
           expected.remove(dt)

        self.assertEqual([], expected)

    def test_iterator_ten_minutes(self):

        start = datetime.datetime(2022, 1, 4, 23, 0, 0)
        end = datetime.datetime(2022, 1, 5, 1, 30, 0)
        delta = datetime.timedelta(minutes=10)

        expected = []

        expected_start = start

        while expected_start <= end:
            expected.append(expected_start)
            expected_start += delta

        for dt in iterate_steps_between_datetimes(start, end, delta):
           expected.remove(dt)

        self.assertEqual([], expected)
