FROM python:3.9-slim
EXPOSE 7000
WORKDIR /app
ADD /deployer/requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ADD /deployer /app