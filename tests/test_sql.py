import unittest
import warnings
from iarp_utils.SQLConnectors import BaseDatabaseConnector, SQLITE
from iarp_utils.exceptions import ImproperlyConfigured


class BaseDBConnTests(unittest.TestCase):
    def test_param_signature_raises_exception(self):
        with self.assertRaises(ImproperlyConfigured):
            db = BaseDatabaseConnector()
            ps = db.param_signature

    def test_connect_raises_notimplemented(self):
        with self.assertRaises(NotImplementedError):
            db = BaseDatabaseConnector()
            db.connect()


class SQLITETests(unittest.TestCase):

    def setUp(self) -> None:
        self.connection = SQLITE()
        self.connection.connect(database=":memory:", isolation_level=None)
        self.cursor = self.connection.cursor

    def tearDown(self) -> None:
        self.connection.close()

    def test_param_signature_does_not_raise(self):
        try:
            ps = self.connection.param_signature
        except ImproperlyConfigured:
            self.fail('param_signature raise ImproperlyConfigured when it should not have.')

    def test_basic_methods_dont_throw_exceptions(self):
        table = 'test_table'
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (blah TEXT)")
        self.connection.insert_item(table, {"blah": "here i am!"})
        self.connection.update_item(table, "blah", "here i am!", {"blah": "i am now this value"})
        self.connection.delete_item(table, "blah", "i am now this value")
        self.connection.truncate_table(table)

    def test_basic_methods_actually_do_things(self):
        table = 'test_table'
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (blah TEXT)")
        self.connection.insert_item(table, {"blah": "here i am!"})

        self.cursor.execute(f'SELECT blah FROM {table}')
        self.assertEqual("here i am!", self.cursor.fetchone()[0])

        self.connection.update_item(table, "blah", "here i am!", {"blah": "i am now this value"})
        self.cursor.execute(f'SELECT blah FROM {table}')
        self.assertEqual("i am now this value", self.cursor.fetchone()[0])

        self.connection.delete_item(table, "blah", "i am now this value")
        self.cursor.execute(f'SELECT blah FROM {table}')
        self.assertIsNone(self.cursor.fetchone())

        self.connection.truncate_table(table)
