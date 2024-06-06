#! /bin/bash

# How to inheret these from parent shell while using `sudo`?
IMDS_ENDPOINT=http://localhost:40342
# IMDS_ENDPOINT=http://host.docker.internal:40342
IDENTITY_ENDPOINT="${IMDS_ENDPOINT}/metadata/identity/oauth2/token"

if [ -z "$IMDS_ENDPOINT" ]; then
  echo "Error: IMDS_ENDPOINT environment variable is not set."
  exit 1
fi

if [ -z "$IDENTITY_ENDPOINT" ]; then
  echo "Error: IMDS_ENDPOINT environment variable is not set."
  exit 1
fi

echo "Identity endpoint: $IDENTITY_ENDPOINT"
MANAGEMENT_ENDPOINT="$IDENTITY_ENDPOINT?api-version=2019-11-01&resource=https%3A%2F%2Fmanagement.azure.com"
echo "Management endpoint: $MANAGEMENT_ENDPOINT"

CHALLENGE_TOKEN_LINE=$(curl -s -D - -H Metadata:true $MANAGEMENT_ENDPOINT | grep Www-Authenticate)
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

# MANAGEMENT_ACCESS_TOKEN_RESPONSE_2=$(curl -s \
#   -H Metadata:true \
#   -H "Authorization: Basic $CHALLENGE_TOKEN" \
#   $MANAGEMENT_ENDPOINT)

# MANAGEMENT_ACCESS_TOKEN_2=$(echo $MANAGEMENT_ACCESS_TOKEN_RESPONSE_2 | jq -r .access_token)
# echo "Magagement Access token: ${MANAGEMENT_ACCESS_TOKEN_2:0:10}...${MANAGEMENT_ACCESS_TOKEN_2: -10}"

CHALLENGE_TOKEN_LINE=$(curl -s -D - -H Metadata:true $MANAGEMENT_ENDPOINT | grep Www-Authenticate)
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
  "${IDENTITY_ENDPOINT}?api-version=2019-11-01&resource=https%3A%2F%2Fcognitiveservices.azure.com")

COGNITIVE_SERVICES_ACCESS_TOKEN=$(echo $COGNITIVE_SERVICES_ACCESS_TOKEN_RESPONSE | jq -r .access_token)
echo "Cognitive Service Access token: ${COGNITIVE_SERVICES_ACCESS_TOKEN:0:10}...${COGNITIVE_SERVICES_ACCESS_TOKEN: -10}"
