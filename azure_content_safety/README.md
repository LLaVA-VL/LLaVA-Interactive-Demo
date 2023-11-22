# Azure AI Content Safety

https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview

## Setup

az login --use-device-code
source set_keys.sh

## Analye Text

```bash
python -m azure_content_safety analyze_text \
    --input_text "Is this text safe?"
```

## Analyze Image

```bash
python -m azure_content_safety analyze_image \
    --image_url "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/contentsafety/azure-ai-contentsafety/samples/sample_data/image.jpg"
```

## Running Tests

```bash
python -m unittest azure_content_safety/tests.py -v
```
