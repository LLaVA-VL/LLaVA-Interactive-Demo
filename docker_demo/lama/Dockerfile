# FROM mcr.microsoft.com/devcontainers/base:ubuntu-20.04
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu20.04

SHELL [ "bash", "-c" ]

ENV DEBIAN_FRONTEND=noninteractive

# update apt and install packages
RUN apt update && \
    apt install -yq \
        ffmpeg \
        dkms \
        build-essential \
        wget

# add git-lfs and install
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash && \
    sudo apt-get install -yq git-lfs && \
    git lfs install

############################################
# Setup user
############################################

# Create user to mimic user from devcontainer image to inherit file permissions from mounted volume
RUN groupadd -g 500000513 appgroup && \
    useradd -u 516398317 -g 500000513 -ms /bin/bash vscode

USER vscode

# Download and install miniconda
RUN cd /tmp && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    rm ./Miniconda3-latest-Linux-x86_64.sh

RUN echo "source ~/miniconda3/bin/activate" >> ~/.bashrc

# Install dotnet
RUN cd /tmp && \
    wget https://dot.net/v1/dotnet-install.sh && \
    chmod +x dotnet-install.sh && \
    ./dotnet-install.sh --channel 7.0 && \
    ./dotnet-install.sh --channel 3.1 && \
    rm ./dotnet-install.sh

RUN echo 'export PATH="$PATH:$HOME/.dotnet"' >> ~/.bashrc

WORKDIR /opt/lama

COPY --chown=vscode lama/conda_env.yml .

RUN source ~/miniconda3/bin/activate && \
    # conda init bash && \
    conda env create -y -n lama -f conda_env.yml && \
    conda activate lama && \
    conda install -y -c pytorch pytorch torchvision torchaudio cudatoolkit=10.2

RUN source ~/miniconda3/bin/activate && \
    conda activate lama && \
    pip install torch==1.10.2+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
    pip install torchvision==0.11.3+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
    pip install flask && \
    pip install pytorch-lightning

# RUN git clone https://huggingface.co/smartywu/big-lama download && \
#     unzip -n -q download/big-lama.zip

ENTRYPOINT ["bash", "docker_demo/lama/start.sh"]
