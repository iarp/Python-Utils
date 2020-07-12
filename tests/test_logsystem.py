import os
import unittest
import shutil

from iarp_utils.logsystem import LogSystem


class LogSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logsystem = LogSystem()

    def tearDown(self) -> None:
        self.logsystem.close()

    def test_basics(self):
        log = self.logsystem.setup_logs('test_basics', write_mode='w')
        string = 'test log entry'
        log.info(string)

    def test_actually_writes(self):
        log = self.logsystem.setup_logs('test_writes', write_mode='w')
        string = 'test log entry'
        log.info(string)
        self.logsystem.close()
        with open(os.path.join(self.logsystem.log_path, 'test_writes.log'), 'r') as fo:
            contents = fo.read()
        self.assertIn(string, contents)

    def test_actually_appends(self):
        log = self.logsystem.setup_logs('test_appends', write_mode='a')
        string = 'test log entry'
        log.info(string)
        self.logsystem.close()
        with open(os.path.join(self.logsystem.log_path, 'test_appends.log'), 'r') as fo:
            contents = fo.read()
        self.assertIn(string, contents)

    def test_logsystem_config_info_works(self):
        self.logsystem = LogSystem(config={'logging': {'level': 'OFF'}})
        log = self.logsystem.setup_logs('test_off', write_mode='w')
        log.info('this entry should not appear in the log file')
        self.logsystem.close()
        with open(os.path.join(self.logsystem.log_path, 'test_off.log'), 'r') as fo:
            contents = fo.read()
        self.assertNotIn('this entry should not appear in the log file', contents)

    def test_logsystem_config_debug_works(self):
        self.logsystem = LogSystem(config={'logging': {'level': 'CRITICAL'}})
        log = self.logsystem.setup_logs('test_debug', write_mode='w')
        log.info('this entry should not appear in the log file')
        self.logsystem.close()
        with open(os.path.join(self.logsystem.log_path, 'test_debug.log'), 'r') as fo:
            contents = fo.read()
        self.assertNotIn('this entry should not appear in the log file', contents)

    def test_logsystem_recall_setup_logs(self):
        self.logsystem = LogSystem(config={'logging': {'level': 'CRITICAL'}})
        log1 = self.logsystem.setup_logs('test_recall', write_mode='w')
        log2 = self.logsystem.setup_logs('test_recall', write_mode='w')
        self.assertEqual(log1, log2)

    def test_logsystem_config_not_dict(self):
        with self.assertRaises(ValueError):
            self.logsystem = LogSystem(config=True)
