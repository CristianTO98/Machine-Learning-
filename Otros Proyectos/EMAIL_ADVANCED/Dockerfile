FROM python:3.9-bullseye

WORKDIR /usr/src/app

COPY requierements.txt ./
RUN pip install --no-cache-dir -r requierements.txt

COPY src/autoscalemaster/worker.py .
COPY src/autoscalemaster/logger.py .

CMD["python", "worket.py"]

