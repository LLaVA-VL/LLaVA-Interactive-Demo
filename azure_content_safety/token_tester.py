import json
from azure.identity import DefaultAzureCredential

from simple_jwt import jwt
# import jwt

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")

print(token.token)

try:
    decoded_token = jwt.decode(token.token)
    # decoded_token = jwt.decode(token.token, algorithms=["RS256"])
    print(json.dumps(decoded_token))
except Exception as e:
    print(f'Error attempting to decode token: {type(e)}\n{str(e)}')
