FROM python:3.9-alpine
EXPOSE 7000
WORKDIR /app 
COPY /deployer /app
RUN pip3 install -r requirements.txt --no-cache-dir
ENTRYPOINT ["python3"] 
CMD ["app.py", "7000"]
 
