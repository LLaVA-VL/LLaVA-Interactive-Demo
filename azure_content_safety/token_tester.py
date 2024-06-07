import json
import jwt
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential()
token = credential.get_token("https://management.azure.com/.default").token

print(token)

try:
    # decoded_token = jwt.decode(token)
    decoded_token = jwt.decode(token, algorithms=["RS256"])
    print(json.dumps(decoded_token))
except Exception as e:
    print(f'Error attempting to decode token: {type(e)}\n{str(e)}')
