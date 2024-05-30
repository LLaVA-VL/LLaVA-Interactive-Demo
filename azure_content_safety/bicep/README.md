# Disable Local Auth for Cognitive Service

## Set Shell Context

```bash
az login --use-device-code

BICEP_FILE_PATH="./azure_content_safety/bicep/disableLocalAuth.bicep"
```

## Verify Resource Access

```bash
az cognitiveservices account show --subscription $EFFICIENT_AI_SUBSCRIPTION_ID -g $RESOURCE_GROUP_NAME -n $CONTENT_SAFETY_NAME --query "{ disableLocalAuth: properties.disableLocalAuth }"
```

## What If Deployment

```bash
az deployment group create \
-f $BICEP_FILE_PATH \
-g $RESOURCE_GROUP_NAME \
-p name=$CONTENT_SAFETY_NAME \
--what-if
```

## Deployment

```bash
az deployment group create `
-f $BICEP_FILE_PATH \
-g $RESOURCE_GROUP_NAME \
-p name=$CONTENT_SAFETY_NAME \
--query "properties.provisioningState" `
-o tsv
```
