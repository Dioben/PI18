FROM python:3.9-alpine
EXPOSE 7000
WORKDIR /app
ADD /deployer/requirements.txt /app/requirements.txt
RUN apk add --update gcc libc-dev fortify-headers linux-headers && rm -rf /var/cache/apk/*
RUN pip3 install -r requirements.txt
ENV BROKER_URL redis://celery_deployer:6380
ENV RESULT_BACKEND redis://celery_deployer:6380
ENV DEPLOYABLE_NAME dioben/nntrackerua-simulation
ENV PARSER_URL http://parser:6000
ENV COMPONENTS timescaledb,grafana,tracker-server,tracker-deployer,tracker-deployer-worker,redis_deployer,tracker-parser,tracker-parser-worker,redis
ADD /deployer /app