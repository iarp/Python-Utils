import unittest

from iarp_utils.strings import startswith_many, endswith_many, slugify, find_between, replace_all, random_character_generator


class StringsTests(unittest.TestCase):

    def test_random_character_generator(self):
        self.assertEqual(5, len(random_character_generator()))
        self.assertEqual(2, len(random_character_generator(length=2)))

    def test_replace_all_simple(self):
        changers = {
            'changed': 'replaced',
        }
        stringer = replace_all('Data I want changed', changers)
        self.assertEqual('Data I want replaced', stringer)

    def test_replace_all_advanced(self):
        changers = {
            'Good Value': ['Bad Value 1', 'Bad Value 2']
        }
        stringer = replace_all('With Bad Value 1 I want changed', changers)
        self.assertEqual('With Good Value I want changed', stringer)

    def test_replace_all_advanced_sub(self):
        changers = {
            'Good Value': ['Bad Value 1', 'Bad Value 2', ['Bad Sub Value 1', 'Bad Sub Value 2']]
        }
        stringer = replace_all('With Bad Sub Value 1 I want changed', changers)
        self.assertEqual('With Good Value I want changed', stringer)

    def test_find_between(self):
        self.assertEqual('here', find_between('[here]', '[', ']'))
        self.assertEqual('here', find_between('data in front [here] data behind', '[', ']'))

    def test_find_between_no_matches(self):
        self.assertEqual('data in front', find_between('data in front', '[', ']'))

    def test_find_between_no_starting(self):
        self.assertEqual('data in front here', find_between('data in front here] data behind', '[', ']'))

    def test_find_between_no_ending(self):
        self.assertEqual('here data behind', find_between('data in front [here data behind', '[', ']'))

    def test_slugify_default(self):
        self.assertEqual('input-with-spaces', slugify('input with spaces'))

    def test_slugify_default_allow_unicode(self):
        self.assertEqual('input-with-spaces', slugify('input with spaces', allow_unicode=True))

    def test_slugify_custom_replace_with(self):
        self.assertEqual('input/with/spaces', slugify('input with spaces', replace_with='/'))

    def test_startswith_many(self):
        string = 'here in stringer'
        matches = ['h', 'he', 'her', 'here']
        self.assertTrue(startswith_many(string, matches))

        self.assertFalse(startswith_many('not in stringer', matches))

        self.assertTrue(startswith_many(string, 'here'))

        with self.assertRaises(TypeError):
            startswith_many(string, {'dict': 'value'})

    def test_endswith_many(self):
        string = 'here in stringer'
        matches = ['nger', 'r', 'er', 'get']
        self.assertTrue(endswith_many(string, matches))

        self.assertFalse(endswith_many('stringer is false', matches))

        self.assertTrue(endswith_many(string, 'stringer'))

        with self.assertRaises(TypeError):
            endswith_many(string, {'dict': 'value'})
