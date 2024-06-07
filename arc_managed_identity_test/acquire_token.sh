#! /bin/bash

if [ -z "$IMDS_ENDPOINT" ]; then
  echo "Error: IMDS_ENDPOINT environment variable is not set."
  exit 1
fi

if [ -z "$IDENTITY_ENDPOINT" ]; then
  echo "Error: IMDS_ENDPOINT environment variable is not set."
  exit 1
fi

echo "IMDS endpoint: $IMDS_ENDPOINT"
echo "IMDS Token endpoint: $IDENTITY_ENDPOINT"
MANAGEMENT_ENDPOINT="$IDENTITY_ENDPOINT?api-version=2019-11-01&resource=https%3A%2F%2Fmanagement.azure.com"
echo "Management endpoint: $MANAGEMENT_ENDPOINT"
COGNITIVE_SERVICES_ENDPOINT="$IDENTITY_ENDPOINT?api-version=2019-11-01&resource=https%3A%2F%2Fcognitiveservices.azure.com"
echo "Cognitive Services endpoint: $COGNITIVE_SERVICES_ENDPOINT"


CHALLENGE_TOKEN_LINE=$(curl -s -D - -H Metadata:true $MANAGEMENT_ENDPOINT | grep -i Www-Authenticate)
# echo "Challenge token line: $CHALLENGE_TOKEN_LINE"
CHALLENGE_TOKEN_PATH=$(echo $CHALLENGE_TOKEN_LINE | cut -d "=" -f 2 | tr -d "[:cntrl:]")
echo "Challenge token path: $CHALLENGE_TOKEN_PATH"

CHALLENGE_TOKEN=$(sudo cat $CHALLENGE_TOKEN_PATH)

if [ $? -ne 0 ]; then
  echo "Could not retrieve challenge token, double check that this command is run with root privileges."
  exit 1
fi

echo "Challenge token read: ${CHALLENGE_TOKEN:0:10}...${CHALLENGE_TOKEN: -10}"

# https://management.azure.com
MANAGEMENT_ACCESS_TOKEN_RESPONSE=$(curl -s \
  -H Metadata:true \
  -H "Authorization: Basic $CHALLENGE_TOKEN" \
  $MANAGEMENT_ENDPOINT)

MANAGEMENT_ACCESS_TOKEN=$(echo $MANAGEMENT_ACCESS_TOKEN_RESPONSE | jq -r .access_token)
echo "Magagement Access token: ${MANAGEMENT_ACCESS_TOKEN:0:10}...${MANAGEMENT_ACCESS_TOKEN: -10}"

CHALLENGE_TOKEN_LINE=$(curl -s -D - -H Metadata:true $COGNITIVE_SERVICES_ENDPOINT | grep -i Www-Authenticate)
CHALLENGE_TOKEN_PATH=$(echo $CHALLENGE_TOKEN_LINE | cut -d "=" -f 2 | tr -d "[:cntrl:]")
echo "Challenge token path: $CHALLENGE_TOKEN_PATH"

CHALLENGE_TOKEN=$(sudo cat $CHALLENGE_TOKEN_PATH)

if [ $? -ne 0 ]; then
  echo "Could not retrieve challenge token, double check that this command is run with root privileges."
  exit 1
fi

echo "Challenge token read: ${CHALLENGE_TOKEN:0:10}...${CHALLENGE_TOKEN: -10}"

# https://cognitiveservices.azure.com/.default"
COGNITIVE_SERVICES_ACCESS_TOKEN_RESPONSE=$(curl -s \
  -H Metadata:true \
  -H "Authorization: Basic $CHALLENGE_TOKEN" \
  $COGNITIVE_SERVICES_ENDPOINT
  )

COGNITIVE_SERVICES_ACCESS_TOKEN=$(echo $COGNITIVE_SERVICES_ACCESS_TOKEN_RESPONSE | jq -r .access_token)
echo "Cognitive Service Access token: ${COGNITIVE_SERVICES_ACCESS_TOKEN:0:10}...${COGNITIVE_SERVICES_ACCESS_TOKEN: -10}"
