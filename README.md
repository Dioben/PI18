## PI18 - Neural Network Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 

This project is licensed under the ***MIT*** license


This project is oriented towards the deployment and management of Neural Networks.

All custom-made components are available as docker images at the following repositories: <br>

[Server](https://hub.docker.com/repository/docker/dioben/nntrackerua-server)<br>
[Individual Simulations](https://hub.docker.com/repository/docker/dioben/nntrackerua-simulation)<br>
[Simulation Deployer](https://hub.docker.com/repository/docker/dioben/nntrackerua-deployer) <br>
[Simulation Output Parser](https://hub.docker.com/repository/docker/dioben/nntrackerua-parser)

<br>
How to run:<br>

```
run.sh
```
<br>
This is equivalent to:<br>

```
docker pull dioben/nntrackerua-simulation:latest
docker-compose up
```
<br>
If the user wants to run the system in detached mode they should use this instead.

The components are connected as follows <br><br>
![deployment diagram](http://xcoa.av.it.pt/~pi202021g08/images/deploymentDiagram.png "Deployment Diagram")
