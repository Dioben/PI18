# Parser Documentation
![alt](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  ![alt](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=whit) 

Component responsible for reporting progress to database

The following environment variables can be set to configure this component:

- DATABASE_PORT: Defaults to 5432
- DATABASE_NAME: Defaults to nntracker
- DATABASE_USER: Defaults to root
- DATABASE_PASSWORD: Defaults to postgres
- BROKER_URL: Link to a redis instance that celery depends on, defaults to redis://redis:6379
- RESULT_BACKEND_URL: Link to where data transfred from host to worker for it to be used, defaults to redis://redis:6379
- DATABASE_HOST: Defaults to timescaledb
