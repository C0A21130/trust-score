# GPU Environment

GPU + PyTorchの環境構築方法について紹介する。以下が環境構成である。
- NVIDIA Graphics Driver：v570
- CUDA：v12.8
- cuDNN：v9
- Nvidia-Container-Toolkit：
- Python：v3.13
- PyTorch：v2.7.1
- PyTorch Geometrics：v2.56.1
- NetworkX：v3.5

## Check Environment

現在のインストールされているグラフィックドライバのバージョンを確認

```bash
nvidia-smi
```

現在のCUDAのバージョンを確認

```bash
nvcc -V
```

パッケージのアップデート

```bash
sudo apt update
sudo apt upgrade -y
```

## Install Nvidia Graphic Driver

最新のグラフィックドライバーのバージョン確認
- ドライバ一覧の中から[recommended]となっているものが推奨である
- 必ずしも推奨バージョンがあっているとは限らないため注意する

```bash
ubuntu-drivers devices
```

過去のドライバーの削除
- 念のため削除後は再起動をする

```bash
sudo apt --purge remove -y nvidia-*
sudo apt --purge remove -y cuda-*
sudo apt --purge remove -y libcudnn-*
sudo apt --purge remove -y cudnn-*
sudo apt autoremove -y
```

グラフィックドライバーのインストール
- DRIVER_VERSIONは確認した最新のグラフィックドライバーから選択した番号を利用する

```bash
sudo apt install nvidia-driver-<DRIVER_VERSION>
sudo reboot
nvidia-smi
```


## Install CUDA

[CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)のインストール
- nvidia-smiで右上に表示されている推奨のCUDAのバージョンをインストールする
- 選択する順番：Linux → x86_64 → Ubuntu → 22.04 → deb(network)

12.8の例

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-8
```

OSを再起動をしてから、CUDAがインストールされていることを確認する
```bash
sudo reboot
nvcc -V
```


## Install cuDNN

cuDNNをインストール
- [インストールリンク](https://developer.nvidia.com/cudnn-downloads)
- Linux → x86_64 → Ubuntu → 22.04 → deb(network)

インストール

```bash
sudo apt-get -y install cudnn-cuda-12
```

インストールの確認

```bash
dpkg -l | grep cudnn
```

## Install nvidia-container-toolkit

DockerでGPUが利用できるようにプラグインをインストールする
- https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
- aptの場合を参照する
- https://ryomo.github.io/notes/nvidia-container-toolkit

レポジトリの設定
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

パッケージリストのアップデート

```bash
sudo apt update-y
```

Toolkitのインストール

```bash
sudo apt-get install -y nvidia-container-toolkit
```

初期設定

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

Dockerの再起動

```bash
sudo systemctl restart docker
```


コンテナでGPUが利用できることを確認する

```bash
docker run --rm --gpus all nvidia/cuda:<CUDA_VERSION>.1-base-ubuntu22.04 nvidia-smi
```

例)

```bash
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

### Example CUDA(12.8.1) + Python(3.13) + PyTorch + PyTorch Geometrics
- Image：Ubuntu22.04 + CUDA
- Install Python3.13
- Install PyTorch
- Install PyTorch Geometrics

例)
```docker
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
```
