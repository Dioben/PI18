<img src ="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
<img src="https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray" />


# Server Documentation


## Rest EndPoints
### Get List of Simulations

**GET ``` /api/simulations/```**\
*Example Value*
```json
{ "simulations":
    [
        {
            "id": 1, 
            "owner":"Rui",
            "name":"Simulation1",
            "model":{},
            "learning_rate":0.001,
            "isdone":false,
            "isrunning":true,
            "layers": 5,
            "epoch_interval":1,
            "goal_epochs":7,
            "metrics":{
                "Accuracy":0.32,
                "BinaryAccuracy":0.01
            },
            "error_text":"",
        },
        {
            "id": 2, 
            "owner":"Rui",
            "name":"Simulation2",
            "model":"{}",
            "learning_rate":0.001,
            "isdone":true,
            "isrunning":false,
            "layers": 2,
            "epoch_interval":1,
            "goal_epochs":4,
            "metrics":{
                "Accuracy":0.12,
                "BinaryAccuracy":0.01
            },
            "error_text":"",
        }
    ]
}
```
- When Not Valid: ``` {} ```
```json
{
  "":0,
  "":"",
  "":"",
  "":"",
  "":[]
}
```
### Get Specific Simulation
**GET ``` /api/simulations/{simulationId}```**\
*Example Value*
```json
{
  "id": 1, 
  "owner":"Rui",
  "name":"Simulation1",
  "model":"{}",
  "learning_rate":0.001,
  "isdone":false,
  "isrunning":true,
  "layers": 5,
  "epoch_interval":1,
  "goal_epochs":7,
  "metrics":{
      "Accuracy":0.32,
      "BinaryAccuracy":0.01
  },
  "error_text":"",
}
```
- When Not Valid: ``` {simulationId} ```
```json
{
  "":0,
  "":"",
  "":"",
  "":"",
  "":[]
}
```
### Manage a Specific Simulation
**POST ``` /api/simulations/{simulationId}/{command}```**

- command: **START** / **STOP** / **PAUSE** 

*Example Return Value*
```json
{
  "id": 1, 
  "owner":"Rui",
  "name":"Simulation1",
  "model":"{}",
  "learning_rate":0.001,
  "isdone":false,
  "isrunning":false,
  "layers": 5,
  "epoch_interval":1,
  "goal_epochs":7,
  "metrics":{
      "Accuracy":0.32,
      "BinaryAccuracy":0.01
  },
  "error_text":"",
}
```
- When Not Valid: ``` {simulationId}/{command} ```
```json
{
  "":0,
  "":"",
  "":"",
  "":"",
  "":[]
}
```