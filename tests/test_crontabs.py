import unittest

from iarp_utils.crontabs import CrontabParser, ParseException


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
