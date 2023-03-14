FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY worker.py .
COPY logger.py .

CMD [ "python3", "worker.py"]

