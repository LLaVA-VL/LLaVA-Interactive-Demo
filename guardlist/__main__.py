import os
import time
import fire
import logging

from .guardlistWrapper import GuardlistWrapper

logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.INFO))

logger = logging.getLogger(__name__)


def analyze_text(
    input_text: str,
    key: str = os.environ["GUARDLIST_KEY"],
    num_requests: int = 1,
    interval_seconds: int = 0,
):
    """Test the Guardlist API.

    :param input_text: Input text to analyze
    :param key: Guardlist Key, defaults to os.environ["GUARDLIST_KEY"]

    Examples

    1. Single request

        ```bash
        python -m guardlist analyze_text \
            --input_text "Is this text safe?"
        ```

    2. 20 requests no delay

        ```bash
        python -m guardlist analyze_text \
            --input_text "Is this text safe?" \
            --num_requests 100
        ```
    """

    assert input_text, "Input text cannot be empty."

    GuardlistWrapper.appKey = key
    GuardlistWrapper.partnerName = "Rate-Limit Tester"

    for i in range(num_requests):
        try:
            is_phrase_problematic = GuardlistWrapper.is_phrase_problematic(input_text, "en")
            logger.info(f"Reqest: {i+1}: Is phrase: '{input_text}' problematic? {'Yes' if is_phrase_problematic else 'No'}")
        except Exception as e:
            logger.error(f"Error: {e}")

        if interval_seconds > 0:
            time.sleep(float(interval_seconds))


if __name__ == "__main__":
    fire.Fire()
