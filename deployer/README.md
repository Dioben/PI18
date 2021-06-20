# Deployer Documentation
![alt](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Component responsible for deploying simulations via Docker UNIX socket, also handles performance information gathering

The following can be configured via environment variables:

- BROKER_URL: link to a redis instance that celery depends on,defaults to redis://celery_deployer:6380
- RESULT_BACKEND: ”i have no idea what this does”, defaults to redis://celery_deployer:6380 
- DEPLOYABLE_NAME: Defaults to dioben/nntrackerua-simulation
- PARSER_URL: Defaults to http://parser:6000 
- COMPONENTS: Comma-separated list of docker containers to be monitored for perfor-mance statistics

The deployer does not commmunicate with the parser, the PARSER_URL variable will be propagated to deployed containers
