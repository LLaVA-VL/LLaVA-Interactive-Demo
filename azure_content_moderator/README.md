# Azure AI Content Moderator

https://learn.microsoft.com/en-us/azure/ai-services/content-moderator/overview

## Setup

az login --use-device-code
source set_keys.sh

## Analye Text

```bash
python -m azure_content_moderator screen_text \
    --text_file_path azure_content_moderator/text_files/email01.txt
```

## Analyze Image

```bash
python -m azure_content_moderator analyze_image \
    --image_url "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/contentsafety/azure-ai-contentsafety/samples/sample_data/image.jpg"
```

