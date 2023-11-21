import os
import time

import fire

from .guardlistWrapper import GuardlistWrapper
from .logger import get_logger

logger = get_logger(__name__)


def analyze_text(
    input_text: str,
    key: str = os.environ["GUARDLIST_KEY"],
    num_requests: int = 1,
    interval_seconds: float = 0,
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

    2. 20 requests 0.25 second delay

        ```bash
        python -m guardlist analyze_text \
            --input_text "Is this text safe?" \
            --num_requests 20 \
            --interval_seconds 0.25
        ```
    """

    assert input_text, "Input text cannot be empty."

    GuardlistWrapper.appKey = key
    GuardlistWrapper.partnerName = "Rate-Limit Tester"

    for i in range(num_requests):
        try:
            is_phrase_problematic = GuardlistWrapper.is_phrase_problematic(input_text, "en")
            logger.info(
                f"Reqest: {i+1:<2} Is phrase: '{input_text}' problematic? {'Yes' if is_phrase_problematic else 'No'}"
            )
        except Exception as e:
            logger.error(f"Error: {e}")

        time.sleep(interval_seconds)


if __name__ == "__main__":
    fire.Fire()
