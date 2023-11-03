import os
import fire
import requests
import base64

from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeTextResult, AnalyzeImageOptions, AnalyzeImageResult, ImageData


def analyze_text(
    input_text: str,
    endpoint: str = os.environ["CONTENT_SAFETY_ENDPOINT"],
    key: str = os.environ["CONTENT_SAFETY_KEY"]
):
    """Test the Azure Content Safety Text API.

    :param input_text: Input text to analyze
    :param endpoint: Content Safety Resource Endpoint, defaults to os.environ["CONTENT_SAFETY_ENDPOINT"]
    :param key: Content Safety Resource Key, defaults to os.environ["CONTENT_SAFETY_KEY"]

    Example:
        ```bash
        python -m azure_content_safety analyze_text \
            --input_text "Is this text safe?"
        ```
    """

    assert input_text, "Input text cannot be empty."

    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
    request = AnalyzeTextOptions(text=input_text)

    # Analyze text
    try:
        response = client.analyze_text(request)
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
            raise
        print(e)
        raise

    print(f'Analyze Text: {input_text}')
    _print_result(response)


def analyze_image(
    image_url: str,
    endpoint: str = os.environ['CONTENT_SAFETY_ENDPOINT'],
    key: str = os.environ['CONTENT_SAFETY_KEY']
):
    """Analyze Image for Content Safety.

    :param image_file_path: File path to image
    :param endpoint: Content Safety Resource Endpoint, defaults to os.environ['CONTENT_SAFETY_ENDPOINT']
    :param key: Content Safety Key, defaults to os.environ['CONTENT_SAFETY_KEY']

    Example:
        ```bash
        python -m azure_content_safety analyze_image \
            --image_url "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/contentsafety/azure-ai-contentsafety/samples/sample_data/image.jpg"
        ```
    """

    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    try:
        response = requests.get(image_url)
        image_bytes = response.content
        image_base64 = base64.b64encode(image_bytes)
        image_base64_str = image_base64.decode('utf-8')
        request = AnalyzeImageOptions(image=ImageData(content=image_base64_str))
        response = client.analyze_image(request)
    except HttpResponseError as e:
        print("Analyze image failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
            raise
        print(e)
        raise

    print(f'Analyze Image: {image_url}')
    _print_result(response)


def _print_result(response: AnalyzeTextResult | AnalyzeImageResult):
    if response.hate_result:
        print(f"Hate severity: {response.hate_result.severity}")
    if response.self_harm_result:
        print(f"SelfHarm severity: {response.self_harm_result.severity}")
    if response.sexual_result:
        print(f"Sexual severity: {response.sexual_result.severity}")
    if response.violence_result:
        print(f"Violence severity: {response.violence_result.severity}")


if __name__ == "__main__":
    fire.Fire()
