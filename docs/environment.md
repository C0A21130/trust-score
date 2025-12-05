# GPU Environment Construction

GPU環境の構築方法について紹介する。
もしTrust-Engineにおける機械学習をCPUではなく、GPUで実施する場合は以下の流れで環境を構築する必要がある。
構成一覧のバージョンは更新されるため適時、変更する必要がある。

**構成一覧**
- NVIDIA Graphics Driver: v580
    - GPUの動作を制御するためのドライバ
- CUDA: v12.8
    - NVIDIAのGPUで並列計算を行うための開発環境
    - PyTorchやcuDNNが内部でGPU計算を行う際に利用
- cuDNN: v9
    - CUDA上で動作するディープラーニング向けの高速ライブラリ
- Nvidia-Container-Toolkit
    - Dockerコンテナ内でGPUを使えるようにするツール

## Advance preparation

現在インストールされているグラフィックドライバのバージョンを確認する。
もしインストールされている場合はグラフィックドライバーのバージョンやGPUの稼働状況が表示される。

```bash
nvidia-smi
```

もし既にグラフィックドライバーがインストールされている場合は削除しクリーンな状態にしておく必要がある

```bash
sudo apt --purge remove -y nvidia-*
sudo apt --purge remove -y cuda-*
sudo apt --purge remove -y libcudnn-*
sudo apt --purge remove -y cudnn-*
sudo apt autoremove -y
```
パッケージの削除後は再起動をする

```bash
sudo reboot
```

パッケージのアップデート

```bash
sudo apt update
sudo apt upgrade -y
```

## Install NVIDIA graphic driver

最新のグラフィックドライバーのバージョン確認する。
ドライバ一覧の中から`recommended`となっているものが推奨されているバージョンである。
しかし利用しているハードウェア環境によって相性に問題が発生する可能性がある。
必ずしも推奨されるバージョンが正しいわけではないので途中でエラーが発生する場合は、異なるバージョンをインストールすることを推奨する。

```bash
ubuntu-drivers devices
```

表示例)
![devices](/docs/images/environment/devices.png)

グラフィックドライバーのインストール
- DRIVER_VERSIONは確認した最新のグラフィックドライバーから選択した番号を利用する

```bash
sudo apt install nvidia-driver-<DRIVER_VERSION> # sudo apt install nvidia-driver-580
sudo reboot
```

インストールしたグラフィックドライバーを確認する。
グラフィックドライバーのバージョンや稼働状況を監視することが可能である。

```bash
nvidia-smi
```

表示例)
![nvidia-smi](/docs/images/environment/smi.png)

## Install CUDA

まず`nvidia-smi`コマンド表示されたステータスの右上に表示されている推奨のCUDAのバージョンを確認する。
確認したバージョンのCUDAのインストールサイトにアクセスし、インストール方法を確認する。
- 最新バージョンの場合は[CUDA Toolkit Downloads](https://developer.nvidia.com/cuda-downloads)にアクセスする
- もし最新バージョン以外の場合は[CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)を参照し最適なバージョンを選択する
- 選択する順番の例：Linux → x86_64 → Ubuntu → 22.04 → deb(network)

13.0の例)

![Select CUDA version](/docs/images/environment/cuda.png)

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-0
```

`/etc/profile`に以下を追加してパスを設定する。
設定するパスは、自身のインストールしたバージョンやディレクトリ環境に合わせる必要がある。

```bash
PATH="/usr/local/cuda-13.0/bin:${PATH}"
export PATH
```

OSを再起動をしてから、CUDAがインストールされていることを確認する

```bash
sudo reboot
nvcc -V
```

## Install cuDNN

cuDNNをインストールする
- [インストールリンク](https://developer.nvidia.com/cudnn-downloads)
- Linux → x86_64 → Ubuntu → 22.04 → deb(network)

cuDNNをインストールする

```bash
sudo apt-get -y install nvidia-cudnn
```

インストールされていることを確認する

```bash
dpkg -l | grep cudnn
```

## Install NVIDIA Container Toolkit

もしDockerのインストールを完了していない場合は、[https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)を参照してインストールする。
インストール後は、管理者(root)権限がなくても実行可能に設定する。

```bash
sudo groupadd docker
sudo gpasswd -a $USER docker
```

DockerでGPUが利用できるようにプラグインをインストールする。
- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)のサイトにアクセスしインストール方法を確認する。
- パッケージマネージャが複数あるため`apt`を参照する
- 参考URL：[https://ryomo.github.io/notes/nvidia-container-toolkit](https://ryomo.github.io/notes/nvidia-container-toolkit)

レポジトリを設定する

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

パッケージリストをアップデートする

```bash
sudo apt update
```

NVIDIA Container Toolkitをインストールする

```bash
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
  sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
```

ツールキットを設定する

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

Dockerを再起動する

```bash
sudo systemctl restart docker
```

コンテナでGPUが利用できることを確認する

```bash
docker run --rm --gpus all nvidia/cuda:<CUDA_VERSION>.1-base-ubuntu22.04 nvidia-smi
```

例)

```bash
docker run --rm --gpus all nvidia/cuda:13.0.1-base-ubuntu22.04 nvidia-smi
```

## Example

以下はDockerを利用してPyTorchの環境を構築する例である

**環境一覧**
- Image：Ubuntu22.04 + CUDA12.8.1
- Python3.12
- PyTorch2.8
- Jupyter Lab

`Dockerfile`を作成する。

```Dockerfile
FROM nvidia/cuda:12.8.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Update packages
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

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir jupyterlab

# Install PyTorch with CUDA 12.8
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
```

`docker-compose`を同じディレクトリに作成する

```yaml
services:
  app:
    build: .
    ports:
      - 8888:8888
    tty: true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

コンテナを起動する

```bash
docker-compose up -d
```
