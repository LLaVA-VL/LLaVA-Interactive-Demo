import os
import unittest
from unittest.mock import patch
from azure.ai.contentsafety import ContentSafetyClient

from .__main__ import _analyze_text, analyze_text


class AnalyzeTextTestCase(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "CONTENT_SAFETY_ENDPOINT": "https://mock-endpoint.cognitiveservices.azure.com/",
            "CONTENT_SAFETY_KEY": "FakeKey",
        },
    )
    def test_analyze_text_0_severities(self):
        input_text = "Is this text safe?"
        expected_input = {'text': input_text}
        expected_result = {
            "_data": {
                "blocklistsMatchResults": [],
                "hateResult": {"category": "Hate", "severity": 0},
                "selfHarmResult": {"category": "SelfHarm", "severity": 0},
                "sexualResult": {"category": "Sexual", "severity": 0},
                "violenceResult": {"category": "Violence", "severity": 0},
            }
        }

        # Mock the analyze_text method of ContentSafetyClient
        with patch.object(ContentSafetyClient, "analyze_text", return_value=expected_result) as mock_analyze_text:
            # Call the analyze_text function
            actual_result = _analyze_text(input_text=input_text)

            # Assert the result
            mock_analyze_text.assert_called_once_with(expected_input)
            self.assertEqual(actual_result, expected_result)

    def test_analyze_text_empty_input(self):
        input_text = ""
        expected_error_message = "Input text cannot be empty."

        # Call the analyze_text function with empty input
        with self.assertRaises(AssertionError) as context:
            analyze_text(input_text)

        # Assert the error message
        self.assertEqual(str(context.exception), expected_error_message)


if __name__ == "__main__":
    unittest.main()
