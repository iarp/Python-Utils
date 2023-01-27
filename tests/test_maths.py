import unittest

from iarp_utils import maths


class MathsTests(unittest.TestCase):

    def test_round_to_nearest_two(self):
        self.assertEqual(0, maths.round_to_nearest(1, 2))
        self.assertEqual(2, maths.round_to_nearest(2, 2))
        self.assertEqual(4, maths.round_to_nearest(3, 2))
        self.assertEqual(4, maths.round_to_nearest(4, 2))

    def test_round_to_nearest_five_down(self):
        self.assertEqual(0, maths.round_to_nearest(0, 5))
        self.assertEqual(0, maths.round_to_nearest(1, 5))
        self.assertEqual(0, maths.round_to_nearest(2, 5))

    def test_round_to_nearest_five_up(self):
        self.assertEqual(5, maths.round_to_nearest(3, 5))
        self.assertEqual(5, maths.round_to_nearest(4, 5))
        self.assertEqual(5, maths.round_to_nearest(5, 5))

    def test_round_to_nearest_ten_down(self):
        for x in range(0, 5+1):
            self.assertEqual(0, maths.round_to_nearest(x, 10), x)

    def test_round_to_nearest_ten_up(self):
        for x in range(6, 10+1):
            self.assertEqual(10, maths.round_to_nearest(x, 10), x)

    def test_round_to_nearest_one_hundred_down(self):
        for x in range(0, 50+1):
            self.assertEqual(0, maths.round_to_nearest(x, 100), x)

    def test_round_to_nearest_one_hundred_up(self):
        for x in range(51, 100+1):
            self.assertEqual(100, maths.round_to_nearest(x, 100), x)
