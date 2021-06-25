## [PI18 - Neural Network Tracker](http://xcoa.av.it.pt/~pi202021g08/)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 

This project is licensed under the ***MIT*** license


This project is oriented towards the deployment and management of Neural Networks.
It provides a database configuration for logging network outputs, including weights, and graphing said outputs.
It includes a web frontend running on port 8000 to ease deployment and management.

All custom-made components are available as docker images at the following repositories: <br>

[Server](https://hub.docker.com/repository/docker/dioben/nntrackerua-server)<br>
[Individual Simulations](https://hub.docker.com/repository/docker/dioben/nntrackerua-simulation)<br>
[Simulation Deployer](https://hub.docker.com/repository/docker/dioben/nntrackerua-deployer) <br>
[Simulation Output Parser](https://hub.docker.com/repository/docker/dioben/nntrackerua-parser)


## Instalation:
docker and docker-compose are necessary to run the system with our default configurations<br>
[Install Docker](https://docs.docker.com/get-docker/)<br>
[Install Docker-Compose](https://docs.docker.com/compose/install/)

## How to run:

Just clone our repository and use

```
./run.sh
```
<br>
This is equivalent to:<br>

```
docker pull dioben/nntrackerua-simulation:latest
docker-compose up
```
<br>

## Default Composition:

The components are connected as follows: <br><br>
![deployment diagram](http://xcoa.av.it.pt/~pi202021g08/images/deploymentDiagram.png "Deployment Diagram")

Components have environment variables that allow for network customization, for more information read the README file associated with the component

## Persistence
By default data is persisted via a TimescaleDB database, following the schema below with the addition of some Django-related tables related to user sessions.
![alt text](https://drive.google.com/uc?export=view&id=1vS_gxdiUgR-utmgHp0C3hA1puDBeicjG)

## Logs
Both meeting logs for all project reunions and work logs detailing the work done by each member can both be found [here](https://github.com/buckaroo69/PI18/blob/main/Logs_PI_G8.pdf)

## Final Report
The final report for the project can be found [here](https://github.com/buckaroo69/PI18/blob/main/Neural_Net_Tracker_Relatorio_Final.pdf)
