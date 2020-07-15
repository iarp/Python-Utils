import unittest
import warnings

from iarp_utils.object_factory import ObjectFactory


class LocalService:
    def __init__(self, location):
        self._location = location

    def test_connection(self):
        print(f'Accessing Local music at {self._location}')


def create_local_music_service(local_music_location):
    return LocalService(local_music_location)


class PandoraService:
    def __init__(self, consumer_key, consumer_secret):
        self._key = consumer_key
        self._secret = consumer_secret

    def test_connection(self):
        print(f'Accessing Pandora with {self._key} and {self._secret}')


class PandoraServiceBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, pandora_client_key=None, pandora_client_secret=None, **_ignored):
        if not self._instance:
            if not pandora_client_key or not pandora_client_secret:
                raise ValueError('Missing pandora_client_key or pandora_client_secret')
            consumer_key, consumer_secret = self.authorize(
                pandora_client_key, pandora_client_secret)
            self._instance = PandoraService(consumer_key, consumer_secret)
        return self._instance

    def authorize(self, key, secret):
        return 'PANDORA_CONSUMER_KEY', 'PANDORA_CONSUMER_SECRET'


class ObjectFactoryTests(unittest.TestCase):

    def setUp(self) -> None:
        self.factory = ObjectFactory()
        self.factory.register('PANDORA', PandoraServiceBuilder())
        self.factory.register('LOCAL', create_local_music_service)

    def test_basic_factory(self):
        expected = 'supplied path'
        b = self.factory('LOCAL', expected)
        self.assertEqual(2, len(self.factory.factories))
        self.assertIsInstance(b, LocalService)
        self.assertEqual(expected, b._location)

    def test_ensure_recall_of_class_type_is_same_instance(self):
        b = self.factory('PANDORA', '1', '2')
        b2 = self.factory('PANDORA')
        self.assertIs(b, b2)

    def test_ensure_recall_of_function_type_is_not_same_instance(self):
        b = self.factory('LOCAL', 'local path 1')
        b2 = self.factory('LOCAL', 'local path 2')
        self.assertIsNot(b, b2)
        self.assertNotEqual(b._location, b2._location)

    def test_basic_factory_with_get(self):
        b = self.factory.get('LOCAL', 'supplied path')
        self.assertIsInstance(b, LocalService)

    def test_basic_factory_not_found(self):
        with self.assertRaises(ObjectFactory.DoesNotExist):
            self.factory('Does Not Exist')

    def test_basic_factory_not_found_with_get(self):
        with self.assertRaises(ObjectFactory.DoesNotExist):
            self.factory.get('Does Not Exist')

    def test_case_insensitive_names(self):
        expected = 'supplied path'
        b = self.factory('local', local_music_location=expected)
        self.assertIsInstance(b, LocalService)
        b = self.factory('Local', local_music_location=expected)
        self.assertIsInstance(b, LocalService)

    def test_adding_existing_factory_already_exists_displays_warning(self):
        with warnings.catch_warnings(record=True) as w:
            self.factory.register('PANDORA', PandoraServiceBuilder())
            self.assertEqual("pandora already exists in ObjectFactory", str(w[-1].message))
