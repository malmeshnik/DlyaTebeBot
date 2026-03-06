import requests

url = "https://chatapi.viber.com/pa/broadcast_message"

headers = {
    "X-Viber-Auth-Token": "",
    "Content-Type": "application/json"
}

data = {
    "broadcast_list": [""],
    "type": "text",
    "text": "test broadcast"
}

r = requests.post(url, json=data, headers=headers)

print(r.json())