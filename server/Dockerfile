FROM python:3.9
WORKDIR /app
COPY /server /app
# COPY . /app            
RUN pip3 install -r requirements.txt --no-cache-dir
ENV ALLOWED_HOSTS localhost,127.0.0.1,0.0.0.0
ENV SELF_PORT 8000
ENV DATABASE_HOST timescaledb
ENV DATABASE_PORT 5432
ENV DATABASE_NAME nntracker
ENV DATABASE_USER root
ENV DATABASE_PASSWORD postgres
ENV GRAFANA_BASE_URL http://localhost:3000
ENV DEPLOYER_BASE_URL http://tracker-deployer:7000
EXPOSE $SELF_PORT
CMD ["sh", "-c", "python3 manage.py runserver 0.0.0.0:$SELF_PORT"]
