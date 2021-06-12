FROM python:3.9
WORKDIR /app
COPY /server /app
# COPY . /app
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["sh", "-c", "python3 manage.py runserver 0.0.0.0:$SELF_PORT"]
