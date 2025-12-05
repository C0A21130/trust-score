FROM nvidia/cuda:12.9.1-cudnn-devel-ubuntu24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv

WORKDIR /build

# ビルドに必要なパッケージをインストール
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    ca-certificates \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    zlib1g-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 3.13.10をインストール
RUN wget https://www.python.org/ftp/python/3.13.10/Python-3.13.10.tar.xz && \
    tar xJf Python-3.13.10.tar.xz && \
    cd Python-3.13.10 && \
    ./configure --enable-optimizations --prefix=/usr/local && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && rm -rf Python-3.13.10*

# 仮想環境の作成
RUN python3.13 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 必要なPythonパッケージをインストール
COPY requirements.txt /build/
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /build/requirements.txt && \
    pip install --no-cache-dir torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu129 && \
    pip install --no-cache-dir torch_geometric && \
    pip install --no-cache-dir pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.8.0+cu129.html

# 軽量なランタイムステージ
FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /trust-engine

# ランタイムに必要な最小限のパッケージのみインストール
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    libsqlite3-0 \
    libssl3t64 \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージからPythonと仮想環境をコピー
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/.venv /app/.venv

# アプリケーションファイルのコピー
COPY app/ /trust-engine/app/

# FastAPI & Jupyter Labの起動
WORKDIR /trust-engine/app
CMD ["bash", "-c", "jupyter-lab --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --no-browser & uvicorn main:app --host 0.0.0.0 --port 9000 --reload"]
