FROM tensorflow/tensorflow
WORKDIR /app 
COPY /simulation /app
#COPY . /app
RUN pip3 install -r requirements.txt --no-cache-dir
ENTRYPOINT ["python3"]
CMD ["app.py"] 
