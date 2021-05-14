FROM tensorflow/tensorflow:nightly
WORKDIR /app 
COPY /simulation /app
RUN pip3 install -r requirements.txt --no-cache-dir
ENTRYPOINT ["python3"]
CMD ["app.py"] 
