import requests
import json

model_json = json.loads(open('model.json','r').read())
conf_json = json.loads(open('conf.json','r').read())
print('Model:',model_json)
print('Configurations:',conf_json)
sent_json = {'model':model_json,'conf':conf_json}
headers = {'Content-type': 'application/json'}
requests.post('http://127.0.0.1:7000/simulations',json = sent_json,headers=headers,timeout=100)