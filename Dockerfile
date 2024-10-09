FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install yfinance
RUN pip install awscli
RUN apt-get update && apt-get install -y curl

COPY broadcom.py .

CMD [ "python3", "broadcom.py"]