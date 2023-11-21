import base64
import os
import time

import fire
import requests
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import (
    AnalyzeImageOptions,
    AnalyzeImageResult,
    AnalyzeTextOptions,
    AnalyzeTextResult,
    ImageData,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from .logger import get_logger

logger = get_logger(__name__, logger_blocklist=["azure", "azure.core", "azure.ai"])


def analyze_text(
    input_text: str,
    endpoint: str = os.environ["CONTENT_SAFETY_ENDPOINT"],
    key: str = os.environ["CONTENT_SAFETY_KEY"],
    num_requests: int = 1,
    interval_seconds: float = 0,
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

        ```bash
        python -m azure_content_safety analyze_text \
            --input_text "Is this text safe?" \
            --num_requests 20 \
            --interval_seconds 0.25
        ```
    """

    assert input_text, "Input text cannot be empty."

    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    for i in range(num_requests):
        try:
            request = AnalyzeTextOptions(text=input_text)
            response = client.analyze_text(request)
        except HttpResponseError as e:
            logger.error("Analyze text failed.")
            if e.error:
                logger.error(f"Error code: {e.error.code}")
                logger.error(f"Error message: {e.error.message}")
                raise

            logger.error(e)
            raise

        logger.info(f'Requst: {i+1:<2} Analyze Text: {input_text}')
        _print_result(response)

        time.sleep(interval_seconds)


def analyze_image(
    image_url: str,
    endpoint: str = os.environ['CONTENT_SAFETY_ENDPOINT'],
    key: str = os.environ['CONTENT_SAFETY_KEY'],
    num_requests: int = 1,
    interval_seconds: float = 0,
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

        ```bash
        python -m azure_content_safety analyze_image \
            --image_url "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/contentsafety/azure-ai-contentsafety/samples/sample_data/image.jpg" \
            --num_requests 20 \
            --interval_seconds 0.25
        ```
    """

    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    for i in range(num_requests):
        try:
            response = requests.get(image_url)
            image_bytes = response.content
            image_base64 = base64.b64encode(image_bytes)
            image_base64_str = image_base64.decode('utf-8')
            request = AnalyzeImageOptions(image=ImageData(content=image_base64_str))
            response = client.analyze_image(request)
        except HttpResponseError as e:
            logger.error("Analyze image failed.")
            if e.error:
                logger.error(f"Error code: {e.error.code}")
                logger.error(f"Error message: {e.error.message}")
                raise
            logger.error(e)
            raise

        logger.info(f'Request: {i+1:<2} Analyze Image: {image_url}')
        _print_result(response)

        time.sleep(interval_seconds)


def _print_result(response: AnalyzeTextResult | AnalyzeImageResult):
    if response.hate_result:
        logger.info(f"Hate severity: {response.hate_result.severity}")
    if response.self_harm_result:
        logger.info(f"SelfHarm severity: {response.self_harm_result.severity}")
    if response.sexual_result:
        logger.info(f"Sexual severity: {response.sexual_result.severity}")
    if response.violence_result:
        logger.info(f"Violence severity: {response.violence_result.severity}")


if __name__ == "__main__":
    fire.Fire()
