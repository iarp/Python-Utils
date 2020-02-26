import os
import sqlite3
import warnings

from .exceptions import ImproperlyConfigured

try:
    import pyodbc
except ImportError:
    pyodbc = None

try:
    import mysql.connector
except ImportError:
    class mysql:
        connector = None


class BaseDatabaseConnector:

    _param_signature = None
    port = None

    def __init__(self):
        self.hostname = ''
        self.database = ''
        self.username = ''
        self.password = ''

        self.connection = None
        self.cursor = None

    @property
    def param_signature(self):
        if not self._param_signature:
            raise ImproperlyConfigured('Classes must implement a _param_signature attribute.')
        return self._param_signature

    def connect(self, hostname='', database='', username='', password='', port=None, **kwargs):
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port or self.port

        # if not database:
        #     warnings.warn('No database supplied, do not forget to USE database.', SyntaxWarning)

        self.connection = self._connect(**kwargs)

        self.cursor = self.connection.cursor()

        if self.database:
            self.use_database(self.database)

        return self.connection

    def _connect(self, **kwargs):
        raise NotImplementedError('_connect must be implemented when extending BaseDatabaseConnector')

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def use_database(self, database):
        self.cursor.execute(f'USE {database}')

    def insert_item(self, table, values):
        """ Insert items into the table supplied

        >>> self.insert_item('TABLE1', {'CONTACT': 'John Doe', 'COMPANY': 'Fred Flintstone'})
        >>> # OR for multiple inserts
        >>> data = [
        >>>     {'CONTACT': 'John Doe', 'COMPANY': 'Fred Flintstone'},
        >>>     {'CONTACT': 'Ronald', 'LASTNAME': 'McDonald'},
        >>> ]
        >>> self.insert_item('TABLE1', data)

        Args:
            table: The table to insert into
            values: A single-level dict OR a list of single level dict's

        Returns:
            Integer counting number of items inserted.
        """
        if not isinstance(values, list):
            values = [values]

        total_inserted = 0
        for row in values:
            question_marks = ','.join(self.param_signature for _ in row.keys())
            columns = ','.join(row.keys())

            query = f"INSERT INTO {table} ({columns}) VALUES ({question_marks})"

            self.cursor.execute(query, list(row.values()))

            if self.cursor.rowcount > 0:
                total_inserted += self.cursor.rowcount

        return total_inserted

    def update_item(self, table: str, where_field: str, record_ids: [str, list], values: dict):
        """ Update items in the database where matching record ids are found.

        >>> data = {'CONTACT': 'Fred Flintstone', 'COMPANY': 'Miners Associated'}
        >>> self.update_item('TABLE1', 'id', '34256', data)
        >>> # OR if you want to update multiple record ids with the same values
        >>> self.update_item('TABLE1', 'id', ['34256', '42563'], data)

        Args:
            table: The table to be updated
            where_field: What column contains record id?
            record_ids: The record id to match against
            values: A single-level dict containing column: value

        Returns:
            Integer counting number of items updated.
        """

        joiner = f'={self.param_signature},'
        query_base = f'{{}}={self.param_signature}'  # {}=?
        query = query_base.format(joiner.join(values.keys()))
        query = f"UPDATE {table} SET {query} WHERE {where_field} = {self.param_signature}"

        if not isinstance(record_ids, list):
            record_ids = [record_ids]

        items = [v for k, v in values.items()]

        total_updated = 0
        for record_id in record_ids:
            items_copied = items.copy()
            items_copied.append(record_id)

            self.cursor.execute(query, items_copied)

            if self.cursor.rowcount > 0:
                total_updated += self.cursor.rowcount

        return total_updated

    def delete_item(self, table: str, where_field: str, record_ids: [str, list]):
        """
         Delete items from the database for specific record ids

        >>> self.delete_item('TABLE1', 'id', '34256')
        >>> # OR to delete multiples
        >>> self.delete_item('TABLE1', 'id', ['34256', '36574'])

        Args:
            table: The table we're deleting from
            where_field: Supply the column to match the record_id value to
            record_ids: List or string containing the record id(s) to be deleted

        Returns:
            Integer counting number of items deleted.
        """
        if not isinstance(record_ids, list):
            record_ids = [record_ids]

        total_deleted = 0
        for record_id in record_ids:
            self.cursor.execute(f'DELETE FROM {table} WHERE {where_field} = {self.param_signature}', (record_id,))

            if self.cursor.rowcount > 0:
                total_deleted += self.cursor.rowcount

        return total_deleted

    def truncate_table(self, table):
        """ Truncate a table in the database

        Args:
            table: The table to truncate.
        """
        self.cursor.execute(f'TRUNCATE TABLE {table}')


class MSSQL(BaseDatabaseConnector):

    _param_signature = '?'
    port = 1433

    def __init__(self):
        super().__init__()
        if pyodbc is None:
            raise ImportError('pyodbc required for SQLServer')

    def _connect(self, **kwargs):

        return pyodbc.connect(
            '',
            driver=kwargs.get('driver', '{SQL Server}'),
            server=self.hostname,
            uid=self.username,
            pwd=self.password,
            port=self.port,
            autocommit=kwargs.get('autocommit', True)
        )  # type: pyodbc.Connection


class MySQL(BaseDatabaseConnector):

    _param_signature = '%s'
    port = 3306

    def __init__(self):
        super().__init__()
        if mysql.connector is None:
            raise ImportError('mysql.connector required for MySQLServer')

    def _connect(self, **kwargs):
        return mysql.connector.connect(
            host=self.hostname,
            user=self.username,
            password=self.password,
            port=self.port,
            buffered=kwargs.get('buffered', False),
            autocommit=kwargs.get('autocommit', True),
            raw=kwargs.get('raw', False)
        )


class SQLITE(BaseDatabaseConnector):

    _param_signature = '?'

    def _connect(self, **kwargs):
        return sqlite3.connect(self.database, **kwargs)  # type: sqlite3.Connection

    def use_database(self, database):
        return True

    def truncate_table(self, table):
        self.cursor.execute(f'DELETE FROM {table} WHERE 1=1')
        self.cursor.execute('VACUUM')
