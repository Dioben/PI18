import requests
import json

data = None
with open("log_pi.json","r") as f:
    data = json.load(f)


print(requests.post("http://localhost:6000/update", json=data))
