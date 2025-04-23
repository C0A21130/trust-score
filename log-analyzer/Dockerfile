FROM nvidia/cuda:12.8.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /log-analyzer

RUN apt-get update -qq && \
    apt-get install -y \
    wget \
    bzip2 \
    build-essential \
    git \
    git-lfs \
    curl \
    ca-certificates \
    libsndfile1-dev \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    zlib1g-dev \
    libopencv-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libgl1 \
    sqlite3 \
    libsqlite3-dev

# Install Python 3.13
RUN wget https://www.python.org/ftp/python/3.12.11/Python-3.12.11.tar.xz && \
    tar xJf Python-3.12.11.tar.xz && \
    cd Python-3.12.11 && \
    ./configure && make && make install
RUN python3 -m venv $VIRTUAL_ENV &&  \
    alias python=$VIRTUAL_ENV/bin/python3 &&  \
    alias pip=$VIRTUAL_ENV/bin/pip3

COPY requirements.txt /log-analyzer/

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /log-analyzer/requirements.txt

# Install PyTorch with CUDA 12.8
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install PyTorch Geometric dependencies
RUN pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.7.0+cu128.html
RUN pip install torch_geometric


CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
