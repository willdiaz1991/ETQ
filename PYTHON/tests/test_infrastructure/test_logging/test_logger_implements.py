import unittest
from unittest.mock import MagicMock, patch

from infrastructure.logging.LoggerImplements import LoggerImplements


class TestLoggerImplements(unittest.TestCase):
    @patch("infrastructure.logging.LoggerImplements.get_logger")
    def setUp(self, mock_get_logger):
        """
        Sets up the test environment by mocking the logger.

        This method uses the `patch` decorator to mock the `get_logger` method,
        which returns a mocked logger instance. The `LoggerImplements` instance
        is then created for use in each test method.

        Args:
            mock_get_logger (MagicMock): Mocked version of the `get_logger` method.
        """
        self.mock_logger = MagicMock()
        mock_get_logger.return_value = self.mock_logger
        self.logger_implements = LoggerImplements("test_logger")

    def test_log_information(self):
        """
        Tests the `log_information` method of `LoggerImplements`.

        This method verifies that the `info` method of the logger is called
        with the correct formatted message when `log_information` is invoked.

        The test checks that the correct parameters, including the message and method name,
        are passed to the logger.

        Asserts:
            - `info` method of the logger is called with the formatted message.
        """
        self.logger_implements.log_information("Test message", "test_method")
        self.mock_logger.info.assert_called_once_with("Method: test_method, Parameters: None, Message: Test message")

    def test_log_error(self):
        """
        Tests the `log_error` method of `LoggerImplements`.

        This method verifies that the `error` method of the logger is called
        with the correct formatted message when `log_error` is invoked.

        The test checks that the correct parameters, including the message and method name,
        are passed to the logger.

        Asserts:
            - `error` method of the logger is called with the formatted message.
        """
        self.logger_implements.log_error("Test error", "test_method")
        self.mock_logger.error.assert_called_once_with("Method: test_method, Parameters: None, Message: Test error")

    def test_log_warning(self):
        """
        Tests the `log_warning` method of `LoggerImplements`.

        This method verifies that the `warning` method of the logger is called
        with the correct formatted message when `log_warning` is invoked.

        The test checks that the correct parameters, including the message and method name,
        are passed to the logger.

        Asserts:
            - `warning` method of the logger is called with the formatted message.
        """
        self.logger_implements.log_warning("Test warning", "test_method")
        self.mock_logger.warning.assert_called_once_with("Method: test_method, Parameters: None, Message: Test warning")

    def test_log_critical(self):
        """
        Tests the `log_critical` method of `LoggerImplements`.

        This method verifies that the `critical` method of the logger is called
        with the correct formatted message when `log_critical` is invoked.

        The test checks that the correct parameters, including the message and method name,
        are passed to the logger.

        Asserts:
            - `critical` method of the logger is called with the formatted message.
        """
        self.logger_implements.log_critical("Test critical", "test_method")
        self.mock_logger.critical.assert_called_once_with("Method: test_method, Parameters: None, Message: Test critical")
