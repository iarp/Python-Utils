import calendar
import datetime
import unittest

from unittest import mock

from iarp_utils.datetimes import weekday, iterate_steps_between_datetimes, get_current_week_of


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


class CurrentWeekOfTests(unittest.TestCase):

    def test_current_week_of_general_value(self):
        with mock.patch('datetime.datetime') as mock_date:
            mock_date.today.return_value = datetime.date(2001, 1, 18)

            self.assertEqual(datetime.date(2001, 1, 15), get_current_week_of(calendar.MONDAY))
            self.assertEqual(datetime.date(2001, 1, 16), get_current_week_of(calendar.TUESDAY))
            self.assertEqual(datetime.date(2001, 1, 17), get_current_week_of(calendar.WEDNESDAY))
            self.assertEqual(datetime.date(2001, 1, 18), get_current_week_of(calendar.THURSDAY))
            self.assertEqual(datetime.date(2001, 1, 12), get_current_week_of(calendar.FRIDAY))
            self.assertEqual(datetime.date(2001, 1, 13), get_current_week_of(calendar.SATURDAY))
            self.assertEqual(datetime.date(2001, 1, 14), get_current_week_of(calendar.SUNDAY))

    def test_current_week_of_general_value_as_passed_param(self):
        date = datetime.date(2001, 1, 18)

        self.assertEqual(datetime.date(2001, 1, 15), get_current_week_of(calendar.MONDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 16), get_current_week_of(calendar.TUESDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 17), get_current_week_of(calendar.WEDNESDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 18), get_current_week_of(calendar.THURSDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 12), get_current_week_of(calendar.FRIDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 13), get_current_week_of(calendar.SATURDAY, date=date))
        self.assertEqual(datetime.date(2001, 1, 14), get_current_week_of(calendar.SUNDAY, date=date))
