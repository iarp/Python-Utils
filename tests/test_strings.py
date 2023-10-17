import unittest

from iarp_utils.strings import slugify, find_between, in_many, replace_all, random_character_generator


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

    def test_in_many_at_least_one_match(self):
        find_within_this = "Show string finale"
        find_one_of_these = [
            " finale",
            " string",
        ]
        self.assertTrue(in_many(find_within_this, find_one_of_these))

    def test_in_many_ensure_space_included(self):
        find_within_this = "Show finale"
        find_one_of_these = [
            " finale",
            " string",
        ]
        self.assertTrue(in_many(find_within_this, find_one_of_these))

    def test_in_many_no_matches(self):
        find_within_this = "showfinale"
        find_one_of_these = [
            " finale",
            " string",
        ]
        self.assertFalse(in_many(find_within_this, find_one_of_these))
