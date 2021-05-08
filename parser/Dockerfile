FROM python:3.9-alpine
EXPOSE 6000
WORKDIR /app 
COPY /parser /app
RUN pip3 install -r requirements.txt --no-cache-dir
ENTRYPOINT ["python3"] 
CMD ["app.py", "6000"] 
