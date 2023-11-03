from pathlib import Path

from azure.cognitiveservices.vision.contentmoderator import \
    ContentModeratorClient
from azure.cognitiveservices.vision.contentmoderator.models import Screen, Evaluate
from msrest.authentication import CognitiveServicesCredentials
from rich import print
import json
import os


client = ContentModeratorClient(
    endpoint=os.environ.get("CONTENT_MODERATOR_ENDPOINT"),
    credentials=CognitiveServicesCredentials(os.environ.get("CONTENT_MODERATOR_KEY"))
)

TEXT_FOLDER_PATH = (Path(__file__).parent / "text_files").resolve()

EMAIL_FILE_PATH = TEXT_FOLDER_PATH / "email01.txt"
with open(EMAIL_FILE_PATH, "rb") as text_fd:
    screen = client.text_moderation.screen_text(
        text_content_type="text/plain",
        text_content=text_fd,
        language="eng",
        autocorrect=True,
        pii=True
    )
    assert isinstance(screen, Screen)
    print(f'Text Moderation: Screen Text Response')
    print(json.dumps(screen.as_dict(), indent=2))


IMAGE_LIST = [
    "https://moderatorsampleimages.blob.core.windows.net/samples/sample2.jpg",
    "https://moderatorsampleimages.blob.core.windows.net/samples/sample5.png"
]

for image_url in IMAGE_LIST:
    print(f"Evaluate image {image_url}")

    evaluation = client.image_moderation.evaluate_url_input(
        content_type="application/json",
        cache_image=True,
        data_representation="URL",
        value=image_url
    )
    assert isinstance(evaluation, Evaluate)

    print(json.dumps(evaluation.as_dict(), indent=2))
    print()
