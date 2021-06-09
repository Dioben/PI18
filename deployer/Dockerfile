FROM python:3.9-alpine
EXPOSE 7000
WORKDIR /app
ADD /deployer/requirements.txt /app/requirements.txt
RUN apk add --update gcc libc-dev fortify-headers linux-headers && rm -rf /var/cache/apk/*
RUN pip3 install -r requirements.txt
ADD /deployer /app