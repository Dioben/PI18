FROM python:3.9-alpine
EXPOSE 7000
WORKDIR /app 
COPY /. /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["flask"] 
CMD ["run", "-p","7000"]
 
