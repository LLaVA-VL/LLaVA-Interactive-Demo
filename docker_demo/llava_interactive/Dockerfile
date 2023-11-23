# FROM mcr.microsoft.com/devcontainers/base:ubuntu-20.04
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu20.04

SHELL [ "bash", "-c" ]

ENV DEBIAN_FRONTEND=noninteractive

# update apt and install packages
RUN apt update && \
    apt install -yq \
        ffmpeg \
        dkms \
        build-essential

# add user tools
RUN sudo apt install -yq \
        jq \
        jp \
        tree \
        tldr \
        iputils-ping \
        wget \
        curl

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

WORKDIR /opt/app

RUN source ~/miniconda3/bin/activate && \
    # conda init bash && \
    conda create -y -n llava_int -c conda-forge -c pytorch python=3.10.8 pytorch=2.0.1 && \
    conda activate llava_int && \
    conda install -y -c nvidia cuda-compiler

COPY --chown=vscode requirements.txt .

RUN source ~/miniconda3/bin/activate && \
    conda activate llava_int && \
    pip install -r requirements.txt

ENTRYPOINT ["bash", "docker_demo/llava_interactive/start.sh"]
