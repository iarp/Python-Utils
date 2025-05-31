import unittest

from iarp_utils.crontabs import *


class CrontabParserTests(unittest.TestCase):

    def test_range_steps_not_enough(self):
        with self.assertRaises(ParseException):
            CrontabParser(24)._range_steps([1])

    def test_parse_star(self):
        self.assertEqual(CrontabParser(24).parse('*'), set(range(24)))
        self.assertEqual(CrontabParser(60).parse('*'), set(range(60)))
        self.assertEqual(CrontabParser(7).parse('*'), set(range(7)))
        self.assertEqual(CrontabParser(31, 1).parse('*'), set(range(1, 31 + 1)))
        self.assertEqual(CrontabParser(12, 1).parse('*'), set(range(1, 12 + 1)))

    def test_parse_range(self):
        self.assertEqual(CrontabParser(60).parse('1-10'), set(range(1, 10 + 1)))
        self.assertEqual(CrontabParser(24).parse('0-20'), set(range(0, 20 + 1)))
        self.assertEqual(CrontabParser().parse('2-10'), set(range(2, 10 + 1)))
        self.assertEqual(CrontabParser(60, 1).parse('1-10'), set(range(1, 10 + 1)))

    def test_parse_range_wraps(self):
        self.assertEqual(CrontabParser(12).parse('11-1'), {11, 0, 1})
        self.assertEqual(CrontabParser(60, 1).parse('2-1'), set(range(1, 60 + 1)))

    def test_parse_groups(self):
        self.assertEqual(CrontabParser().parse('1,2,3,4'), {1, 2, 3, 4})
        self.assertEqual(CrontabParser().parse('0,15,30,45'), {0, 15, 30, 45})
        self.assertEqual(CrontabParser(min_=1).parse('1,2,3,4'), {1, 2, 3, 4})

    def test_parse_steps(self):
        self.assertEqual(CrontabParser(8).parse('*/2'), {0, 2, 4, 6})
        self.assertEqual(CrontabParser().parse('*/2'), {i * 2 for i in range(30)})
        self.assertEqual(CrontabParser().parse('*/3'), {i * 3 for i in range(20)})
        self.assertEqual(CrontabParser(8, 1).parse('*/2'), {1, 3, 5, 7})
        self.assertEqual(CrontabParser(min_=1).parse('*/2'), {
            i * 2 + 1 for i in range(30)
        })
        self.assertEqual(CrontabParser(min_=1).parse('*/3'), {
            i * 3 + 1 for i in range(20)
        })

    def test_parse_composite(self):
        self.assertEqual(CrontabParser(8).parse('*/2'), {0, 2, 4, 6})
        self.assertEqual(CrontabParser().parse('2-9/5'), {2, 7})
        self.assertEqual(CrontabParser().parse('2-10/5'), {2, 7})
        self.assertEqual(CrontabParser(min_=1).parse('55-5/3'), {55, 58, 1, 4})
        self.assertEqual(CrontabParser().parse('2-11/5,3'), {2, 3, 7})
        self.assertEqual(CrontabParser().parse('2-4/3,*/5,0-21/4'), {
            0, 2, 4, 5, 8, 10, 12, 15, 16, 20, 25, 30, 35, 40, 45, 50, 55,
        })
        self.assertEqual(CrontabParser().parse('1-9/2'), {1, 3, 5, 7, 9})
        self.assertEqual(CrontabParser(8, 1).parse('*/2'), {1, 3, 5, 7})
        self.assertEqual(CrontabParser(min_=1).parse('2-9/5'), {2, 7})
        self.assertEqual(CrontabParser(min_=1).parse('2-10/5'), {2, 7})
        self.assertEqual(CrontabParser(min_=1).parse('2-11/5,3'), {2, 3, 7})
        self.assertEqual(CrontabParser(min_=1).parse('2-4/3,*/5,1-21/4'), {
            1, 2, 5, 6, 9, 11, 13, 16, 17, 21, 26, 31, 36, 41, 46, 51, 56,
        })
        self.assertEqual(CrontabParser(min_=1).parse('1-9/2'), {1, 3, 5, 7, 9})

    def test_parse_errors_on_empty_string(self):
        with self.assertRaises(ParseException):
            CrontabParser(60).parse('')

    def test_parse_errors_on_empty_group(self):
        with self.assertRaises(ParseException):
            CrontabParser(60).parse('1,,2')

    def test_parse_errors_on_empty_steps(self):
        with self.assertRaises(ParseException):
            CrontabParser(60).parse('*/')

    def test_parse_errors_on_negative_number(self):
        with self.assertRaises(ParseException):
            CrontabParser(60).parse('-20')

    def test_parse_errors_on_lt_min(self):
        CrontabParser(min_=1).parse('1')
        with self.assertRaises(ValueError):
            CrontabParser(12, 1).parse('0')
        with self.assertRaises(ValueError):
            CrontabParser(24, 1).parse('12-0')

    def test_parse_errors_on_gt_max(self):
        CrontabParser(1).parse('0')
        with self.assertRaises(ValueError):
            CrontabParser(1).parse('1')
        with self.assertRaises(ValueError):
            CrontabParser(60).parse('61-0')

    def test_day_of_week_includes_zero_through_seven(self):
        *_, day_of_week = parse('* * * * *')
        self.assertEqual(day_of_week, {0, 1, 2, 3, 4, 5, 6, 7})

    def test_day_of_week_as_text(self):
        self.assertEqual(CrontabParser(7).parse('mon'), {1})
        self.assertEqual(CrontabParser(7).parse('monday'), {1})
        self.assertEqual(CrontabParser(7).parse('tues'), {2})
        self.assertEqual(CrontabParser(7).parse('mon-fri'), {1, 2, 3, 4, 5})
        with self.assertRaises(ValueError):
            CrontabParser(7).parse('invalid')

        m, h, d, month, day_of_week = parse('* * mon-fri * tues-thurs')
        self.assertEqual(d, {1, 2, 3, 4, 5})
        self.assertEqual(day_of_week, {2, 3, 4})

    def test_weekday_by_name_into_number(self):
        days = 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'
        for index, day in zip(range(0, 6, 1), days):
            self.assertEqual(index, weekday(day))

        with self.assertRaises(KeyError):
            weekday('weekday that does not exist')

    def test_validate_crontab_values_minute(self):

        self.assertTrue(validate_crontab_values(minute=0))
        self.assertTrue(validate_crontab_values(minute=10))
        self.assertTrue(validate_crontab_values(minute=20))
        self.assertTrue(validate_crontab_values(minute=30))
        self.assertTrue(validate_crontab_values(minute=40))
        self.assertTrue(validate_crontab_values(minute=50))

        def check_valueerror_raised(value):

            for x in range(value, 60, 10):
                with self.assertRaisesRegex(ValueError, 'divisible by 10'):
                    validate_crontab_values(minute=x)

        check_valueerror_raised(1)
        check_valueerror_raised(2)
        check_valueerror_raised(3)
        check_valueerror_raised(4)
        check_valueerror_raised(5)
        check_valueerror_raised(6)
        check_valueerror_raised(7)
        check_valueerror_raised(8)
        check_valueerror_raised(9)

        with self.assertRaisesRegex(ValueError, 'between 0-59'):
            validate_crontab_values(minute=60)

    def test_validate_crontab_values_hour(self):
        for x in range(0, 23, 1):
            self.assertTrue(validate_crontab_values(hour=x))

        with self.assertRaisesRegex(ValueError, 'between 0-23'):
            validate_crontab_values(hour=24)

    def test_validate_crontab_values_day_of_week(self):
        for x in range(0, 6):
            self.assertTrue(validate_crontab_values(day_of_week=x))

        with self.assertRaisesRegex(ValueError, 'between 0-6'):
            validate_crontab_values(day_of_week=7)

    def test_validate_crontab_values_day_of_month(self):
        for x in range(1, 31):
            self.assertTrue(validate_crontab_values(day_of_month=x))

        with self.assertRaisesRegex(ValueError, 'between 1-31'):
            validate_crontab_values(day_of_month=0)
        with self.assertRaisesRegex(ValueError, 'between 1-31'):
            validate_crontab_values(day_of_month=32)

    def test_validate_on_all_crontab_generator_functions(self):
        with self.assertRaisesRegex(ValueError, 'divisible by 10'):
            generate_daily(minute=12)
        with self.assertRaisesRegex(ValueError, 'divisible by 10'):
            generate_weekly(minute=12)
        with self.assertRaisesRegex(ValueError, 'divisible by 10'):
            generate_monthly(minute=12)
        with self.assertRaisesRegex(ValueError, 'divisible by 10'):
            generate_biyearly(minute=12)
        with self.assertRaisesRegex(ValueError, 'divisible by 10'):
            generate_yearly(minute=12)

    def test_generate_daily(self):
        output = generate_daily(minute=10, hour=2)
        self.assertEqual('10 2 * * *', output)
        output = generate_daily(minute=10, hour=[2,3])
        self.assertRegex(output, r'^10 [2,3] \* \* \*$')

    def test_generate_every_other_day(self):
        output = generate_every_other_day(minute=10, hour=2)
        self.assertRegex(output, r'^10 2 \* \* (0-7\/2|1-7\/2)$')
        output = generate_every_other_day(minute=10, hour=[2,3])
        self.assertRegex(output, r'^10 [2,3] \* \* (0-7\/2|1-7\/2)$')

    def test_generate_weekly(self):
        output = generate_weekly(minute=10, hour=2, day_of_week=6)
        self.assertEqual('10 2 * * 6', output)

        output = generate_weekly(minute=10, hour=[2, 3], day_of_week=6)
        self.assertRegex(output, r'^10 [2,3] \* \* 6$')

        output = generate_weekly(minute=10, hour=[2, 3], day_of_week=None)
        self.assertRegex(output, r'^10 [2,3] \* \* [0-7]$')

    def test_generate_weekly_multiple_days(self):
        output = generate_weekly(minute=10, hour=[2, 3], day_of_week=[3,6])
        self.assertRegex(output, r'^10 [2,3] \* \* [3,6]$')

    def test_generate_monthly(self):
        output = generate_monthly(minute=10, hour=2, day=4)
        self.assertEqual('10 2 4 * *', output)

        output = generate_monthly(minute=10, hour=[2, 3], day=4)
        self.assertRegex(output, r'^10 [2,3] 4 \* \*$')

    def test_generate_biyearly(self):
        output = generate_biyearly(minute=10, hour=2, day=4)
        self.assertRegex(output, r'^10 2 4 \d{1,2},\d{1,2} \*$')

        output = generate_biyearly(minute=10, hour=[2, 3], day=4)
        self.assertRegex(output, r'^10 [2,3] 4 \d{1,2},\d{1,2} \*$')

    def test_generate_yearly(self):
        output = generate_yearly(minute=10, hour=2, day=4)
        self.assertRegex(output, r'^10 2 4 \d+ \*$')

        output = generate_yearly(minute=10, hour=[2, 3], day=4)
        self.assertRegex(output, r'^10 [2,3] 4 \d+ \*$')

    def test_generate_selection_monthly_crontabs(self):
        output = generate_selection_monthly_crontabs(length=8)
        self.assertEqual(8, len(output))

        re_days = "|".join(f"{x}" for x in range(32))

        self.assertRegex(output[0], fr'0 5 [{re_days}] * *')
        self.assertRegex(output[1], fr'10 5 [{re_days}] * *')
        self.assertRegex(output[2], fr'20 5 [{re_days}] * *')
        self.assertRegex(output[3], fr'30 5 [{re_days}] * *')
        self.assertRegex(output[4], fr'40 5 [{re_days}] * *')
        self.assertRegex(output[5], fr'50 5 [{re_days}] * *')
        self.assertRegex(output[6], fr'0 6 [{re_days}] * *')
        self.assertRegex(output[7], fr'10 6 [{re_days}] * *')

    def test_generate_selection_biweekly_crontabs(self):
        output = generate_selection_biweekly_crontabs(length=8)
        self.assertEqual(8, len(output))

        re_days_first = "|".join(f"{x}" for x in range(1, 15))
        re_days_second = "|".join(f"{x}" for x in range(14, 31))

        self.assertRegex(output[0], fr'0 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[1], fr'10 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[2], fr'20 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[3], fr'30 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[4], fr'40 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[5], fr'50 13 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[6], fr'0 14 [{re_days_first},{re_days_second}] * *')
        self.assertRegex(output[7], fr'10 14 [{re_days_first},{re_days_second}] * *')

    def test_generate_selection_daily_crontabs(self):
        output = generate_selection_daily_crontabs(length=8)
        self.assertEqual(8, len(output))

        self.assertEqual('0 16 * * *', output[0])
        self.assertEqual('10 16 * * *', output[1])
        self.assertEqual('20 16 * * *', output[2])
        self.assertEqual('30 16 * * *', output[3])
        self.assertEqual('40 16 * * *', output[4])
        self.assertEqual('50 16 * * *', output[5])
        self.assertEqual('0 17 * * *', output[6])
        self.assertEqual('10 17 * * *', output[7])
