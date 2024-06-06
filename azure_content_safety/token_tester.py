import json
from azure.identity import DefaultAzureCredential
import jwt
import httpx

# credential = DefaultAzureCredential()
# token = credential.get_token("https://management.azure.com/.default").token

# Get token from IMDS proxy running on host machine outside container
token_response = httpx.get("http://host.docker.internal:8000/token")
token = token_response.json()["access_token"]
print(token)

try:
    # decoded_token = jwt.decode(token)
    decoded_token = jwt.decode(token, algorithms=["RS256"])
    print(json.dumps(decoded_token))
except Exception as e:
    print(f'Error attempting to decode token: {type(e)}\n{str(e)}')
