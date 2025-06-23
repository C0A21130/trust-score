FROM python:3.13-slim

ENV TZ Asia/Tokyo

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y build-essential libffi-dev

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
