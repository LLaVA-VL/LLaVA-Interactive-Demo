import os
import fire
import json

from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeTextResult


def analyze_text(
        input_text: str,
        endpoint: str = os.environ["CONTENT_SAFETY_ENDPOINT"],
        key: str = os.environ["CONTENT_SAFETY_KEY"]
        ):
    """Test the Azure Content Safety Text API.

    :param input_text: Input text to analyze
    :param endpoint: Content Safety Resource Endpoint, defaults to os.environ["CONTENT_SAFETY_ENDPOINT"]
    :param key: Content Safety Resource Key, defaults to os.environ["CONTENT_SAFETY_KEY"]
    """

    assert input_text, "Input text cannot be empty."

    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
    request = AnalyzeTextOptions(text=input_text)

    # Analyze text
    try:
        response: AnalyzeTextResult = client.analyze_text(request)
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
            raise
        print(e)
        raise

    if response.hate_result:
        print(f"Hate severity: {response.hate_result.severity}")
    if response.self_harm_result:
        print(f"SelfHarm severity: {response.self_harm_result.severity}")
    if response.sexual_result:
        print(f"Sexual severity: {response.sexual_result.severity}")
    if response.violence_result:
        print(f"Violence severity: {response.violence_result.severity}")


if __name__ == "__main__":
    fire.Fire(analyze_text)
