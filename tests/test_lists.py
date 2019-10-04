import unittest

from iarp_utils.lists import chunks


class ListsTests(unittest.TestCase):

    def test_chunks_correctly(self):
        items = [1,2,3,4,5,6]
        i, c = 0, 0
        for chunk in chunks(items, 2):
            i += 1
            c += len(chunk)
        self.assertEqual(3, i)
        self.assertEqual(len(items), c)
