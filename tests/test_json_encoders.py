import json
import unittest

from iarp_utils import json_encoders


class JSONEncodersTests(unittest.TestCase):
    def test_does_not_raise_exception_with_set(self):
        data = {'test': set()}
        try:
            json.dumps(data, cls=json_encoders.JSONSetToListEncoder)
        except TypeError:
            self.fail('JSONSetEncoder failed to convert set to list')

    def test_base_json_raises_exception_with_set(self):
        data = {'test': set()}

        with self.assertRaises(TypeError, msg="json.dumps converted set to list, that currently is not possible."):
            json.dumps(data)
