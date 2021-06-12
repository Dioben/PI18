FROM python:3.9
EXPOSE 6000
WORKDIR /app 
#COPY . /app
COPY /parser /app
RUN pip3 install -r requirements.txt --no-cache-dir
ENV DATABASE_HOST timescaledb
ENV DATABASE_PORT 5432
ENV DATABASE_NAME nntracker
ENV DATABASE_USER root
ENV DATABASE_PASSWORD postgres
