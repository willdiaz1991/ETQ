import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from infrastructure.logging.logger import CustomTZFormatter, get_logger


class TestGetLogger(unittest.TestCase):

    @patch("infrastructure.logging.logger.logging.getLogger")
    def test_get_logger_configures_logger(self, mock_get_logger):
        """
        Test that get_logger correctly initializes and configures a logger
        when no handlers are present.

        This includes:
        - Setting the log level
        - Attaching a StreamHandler
        - Applying a CustomTZFormatter with the correct timezone offset
        - Disabling propagation
        """
        mock_logger = MagicMock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger
        mock_logger.handlers = []

        logger = get_logger("my_logger", level=logging.INFO, tz_offset_hours=-3)

        mock_get_logger.assert_called_once_with("my_logger")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logger.addHandler.assert_called_once()
        self.assertEqual(logger, mock_logger)
        self.assertFalse(logger.propagate)

        handler = mock_logger.addHandler.call_args[0][0]
        self.assertIsInstance(handler.formatter, CustomTZFormatter)
        self.assertEqual(handler.formatter.tz.utcoffset(None).total_seconds(), -3 * 3600)

    def test_custom_tz_formatter_format_time(self):
        """
        Test that CustomTZFormatter.formatTime correctly formats a timestamp
        using the specified timezone offset and date format.
        """
        timestamp = 1721900000.0
        record = MagicMock()
        record.created = timestamp

        formatter = CustomTZFormatter(tz_offset_hours=-5, datefmt="%Y-%m-%d %H:%M:%S")
        formatted_time = formatter.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")

        expected_time = datetime.fromtimestamp(timestamp, timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S")

        self.assertEqual(formatted_time, expected_time)
