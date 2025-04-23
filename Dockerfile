FROM python:3.12.8

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt update -qq && \
    apt install -y \
    wget \
    bzip2 \
    build-essential \
    git \
    git-lfs \
    curl \
    ca-certificates \
    libsndfile1-dev \
    libgl1 \
    python3 \
    python3-pip

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -U pip && pip3 install --no-cache-dir -r requirements.txt

CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
