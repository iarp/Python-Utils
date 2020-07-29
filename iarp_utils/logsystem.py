import datetime
import logging
import logging.handlers
import os

from . import configuration, strings


class LogSystem:
    """ Setup logging with minimal code.

    Examples:

        >>> ls = LogSystem()
        >>> log = ls.setup_logs('scriptname')
        >>> log.info('this info is logged!')

    """

    def __init__(self, level=None, log_path=None, config_file='setup/config.json', config=None, **kwargs):
        self.log_path = log_path
        self.level = level
        self.handlers = []

        # This variable controls whether or not logging is enabled or disabled.
        self.propagate = kwargs.pop('propagate', True)

        if not config:
            config = configuration.load(config_file)
        elif not isinstance(config, dict):
            raise ValueError('config must be dict')

        # If no level is supplied attempt to load one from config
        if self.level is None:
            config_level = config.get('logging', {}).get('level')
            if config_level is not None:
                disabled_levels = ['OFF', 'DISABLE', 'DISABLED', '0', 'FALSE']
                if not config_level or (isinstance(config_level, str) and config_level.upper() in disabled_levels):
                    self.propagate = False
                    self.level = logging.CRITICAL
                elif isinstance(config_level, str):
                    self.level = getattr(logging, config_level.upper(), None)
                elif isinstance(config_level, int) and 0 <= config_level <= 50:
                    self.level = config_level

        if not self.level:
            self.level = logging.DEBUG

        # If we were not given a path to save the logs to attempt to load one from config.
        if self.log_path is None:
            self.log_path = config.get('logging', {}).get('save_path', None)

        # If we were not given a path and config does not contain one this is our default path.
        if not self.log_path:
            self.log_path = os.path.join(os.path.abspath('logs'), '{{date}}')

        # These are dynamic variables allowed in the log path.
        now = datetime.datetime.now()
        self.log_path = strings.replace_all(self.log_path, {
            '{{date}}': now.strftime('%Y-%m-%d'),
            '{{time}}': now.strftime('%H%M%S'),
            '{{datetime}}': now.strftime('%Y-%m-%d %H%M%S'),
        })

        os.makedirs(self.log_path, exist_ok=True)

    def close(self):
        for handler in self.handlers:
            handler.close()

    def setup_logs(self, logger_name, write_mode='a', write_to_console=True, write_to_file=True,
                   file_formatter='%(asctime)s - %(levelname)s - %(message)s',
                   console_formatter='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=None, propagate=None):
        """ Returns a logger object that will log to the logger_name.log filename given.

        Args:
            logger_name: Name of the logging object, must be unique, used for the log filename too.
            write_mode: w or a for write or append
            write_to_console: Whether or not to print to console.
            write_to_file: Whether or not to write to a file.
            file_formatter: Log handler formatter for writing to the file
            console_formatter: Log handler formatter for writing to console.
            level: Log level, overriding the initial configuration setting.
            propagate: Log propagate, overriding the initial configuration setting.

        Returns:
            logging.getLogger
        """

        log = logging.getLogger(logger_name)

        # If this log already has handlers, just return the object.
        # If we did not check this and added another file/stream handler then it X's the output
        #   depending on how many times the handlers were added to a single logging object.
        if log.handlers:
            return log

        log.propagate = self.propagate if propagate is None else propagate
        log.setLevel(level or self.level)

        if write_to_file:
            log_file = os.path.join(self.log_path, '{}.log'.format(logger_name))

            file_handler = logging.FileHandler(log_file, mode='w')
            if write_mode.lower() in ['a', 'append']:
                file_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760, backupCount=3)

            file_formatter = logging.Formatter(file_formatter)
            file_handler.setFormatter(file_formatter)

            log.addHandler(file_handler)
            self.handlers.append(file_handler)

        if write_to_console:
            stream_formatter = logging.Formatter(console_formatter, "%H:%M:%S")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(stream_formatter)

            log.addHandler(stream_handler)
            self.handlers.append(stream_handler)

        return log
