import requests

import requests

url = "http://64.226.68.161/api/v1/supervisor/seller/sales/25841/01112025/"

headers = {
    "Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxNTY5NywiZW1haWwiOiJhbGVua2ExM3JnQHVrci5uZXQiLCJ1c2VybmFtZSI6IiszODA2MzI3MzQyNzUiLCJleHAiOjE3NjM0NTc1MzcsInBob25lIjoiKzM4MDYzMjczNDI3NSJ9.f559EqWErrpBAZg5vPm3yF4Du9wMI3CMsJBXSFLmwdI",
    "Accept": "*/*"
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)
print("Response:")
print(response.text)
