FROM python:3.9
EXPOSE 8000
WORKDIR /app 
# COPY . /app
COPY /server /app
RUN pip3 install -r requirements.txt --no-cache-dir 
ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
