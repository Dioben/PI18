import requests
import json

data = None
with open("log_pi.json","r") as f:
    data = json.load(f)


requests.post("http://127.0.0.1:5000/update",json=data)
