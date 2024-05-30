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

```powershell
Install-Module -Force Az.CognitiveServices
Connect-AzAccount -UseDeviceAuthentication
Set-azcontext -subscription $EFFICIENT_AI_SUBSCRIPTION_ID
Set-AzCognitiveServicesAccount -ResourceGroupName $RESOURCE_GROUP_NAME -Name $CONTENT_SAFETY_NAME -DisableLocalAuth $true -WhatIf
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

## Other

```bash
RESOURCE_ID=$(az cognitiveservices account show --subscription $EFFICIENT_AI_SUBSCRIPTION_ID -g $RESOURCE_GROUP_NAME -n $CONTENT_SAFETY_NAME --query "id" -o tsv)
az role assignment list --assignee "SC-mr332@microsoft.com" --scope $RESOURCE_ID
az role assignment list --assignee $CONTENT_SAFETY_APP_ID --scope $RESOURCE_ID --query "[].roleDefinitionName"
az role assignment list --assignee $LLAVA_INTERACTIVE_CLIENT_ID --scope $RESOURCE_ID --query "[].roleDefinitionName"
```
