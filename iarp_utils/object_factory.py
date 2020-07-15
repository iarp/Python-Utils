import warnings


class ObjectFactory:
    """
        https://realpython.com/factory-method-python/#recognizing-opportunities-to-use-factory-method

    Examples::

        class LocalService:
            def __init__(self, location):
                self._location = location

            def test_connection(self):
                print(f'Accessing Local music at {self._location}')

        def create_local_music_service(local_music_location, **_ignored):
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

        factory = ObjectFactory()
        factory.register('PANDORA', PandoraServiceBuilder())
        factory.register('LOCAL', create_local_music_service)

        item = factory.get('PANDORA', pandora_client_key='...', pandora_client_secret='...')
        item.test_connection()

        or you can do the following

        item = factory('PANDORA', pandora_client_key='...', pandora_client_secret='...')
        item.test_connection()
    """

    class DoesNotExist(Exception):
        pass

    def __init__(self):
        self.factories = {}

    def register(self, name: str, builder):
        name = name.lower()

        if name in self.factories:
            warnings.warn(f'{name} already exists in {type(self).__name__}')

        self.factories[name] = builder

    def get(self, name: str, *args, **kwargs):
        try:
            return self.factories[name.lower()](*args, **kwargs)
        except KeyError:
            raise self.DoesNotExist(name)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)
