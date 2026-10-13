import unittest

from api.response.api_response import ApiResponse


class TestApiResponse(unittest.TestCase):
    """
    Unit tests for the ApiResponse class. These tests validate the behavior of the
    ApiResponse factory methods: `create_successful`, `create_unsuccessful`, and `create_error`.
    """

    def test_create_successful(self):
        """
        Tests the `create_successful` method of the ApiResponse class.

        This method is expected to:
            - Return an ApiResponse object with the `is_successful` attribute set to True.
            - Return the provided `result` as the value for the `result` attribute.
            - Ensure that `error_message` and `messages` are both set to None.

        Verifies that the returned response has the correct attributes set for a successful result.
        """
        result = {"key": "value"}
        response = ApiResponse.create_successful(result)

        self.assertTrue(response.is_successful)
        self.assertFalse(response.is_error)
        self.assertEqual(response.result, result)
        self.assertIsNone(response.error_message)
        self.assertIsNone(response.messages)

    def test_create_unsuccessful(self):
        """
        Tests the `create_unsuccessful` method of the ApiResponse class.

        This method is expected to:
            - Return an ApiResponse object with the `is_successful` attribute set to False.
            - Set the `messages` attribute to the provided list of messages.
            - Ensure that `error_message` and `result` are both set to None.

        Verifies that the returned response has the correct attributes set for an unsuccessful result.
        """
        messages = ["Error message"]
        response = ApiResponse.create_unsuccessful(messages)

        self.assertFalse(response.is_successful)
        self.assertFalse(response.is_error)
        self.assertEqual(response.messages, messages)
        self.assertIsNone(response.error_message)
        self.assertIsNone(response.result)

    def test_create_error(self):
        """
        Tests the `create_error` method of the ApiResponse class.

        This method is expected to:
            - Return an ApiResponse object with the `is_successful` attribute set to False.
            - Set the `is_error` attribute to True.
            - Set the `error_message` attribute to the provided error message.
            - Ensure that `messages` and `result` are both set to None.

        Verifies that the returned response has the correct attributes set for an error result.
        """
        error_message = "An error occurred"
        response = ApiResponse.create_error(error_message)

        self.assertFalse(response.is_successful)
        self.assertTrue(response.is_error)
        self.assertEqual(response.error_message, error_message)
        self.assertIsNone(response.messages)
        self.assertIsNone(response.result)
