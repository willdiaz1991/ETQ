from infrastructure.logging.logger import get_logger


class LoggerImplements:
    def __init__(self, name: str):
        self._logger = get_logger(name)

    def log_information(self, message: str, method: str, parameters: str = None):
        self._logger.info(f"Method: {method}, Parameters: {parameters}, Message: {message}")

    def log_error(self, message: str, method: str, parameters: str = None):
        self._logger.error(f"Method: {method}, Parameters: {parameters}, Message: {message}")

    def log_warning(self, message: str, method: str, parameters: str = None):
        self._logger.warning(f"Method: {method}, Parameters: {parameters}, Message: {message}")

    def log_critical(self, message: str, method: str, parameters: str = None):
        self._logger.critical(f"Method: {method}, Parameters: {parameters}, Message: {message}")
