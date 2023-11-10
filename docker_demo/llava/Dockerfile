# Use the nvidia/cuda image as the base image
FROM mcr.microsoft.com/devcontainers/base:ubuntu-20.04
# FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

SHELL [ "bash", "-c" ]

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

USER vscode

# Download and install miniconda
RUN cd /tmp && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    rm ./Miniconda3-latest-Linux-x86_64.sh

RUN echo "source ~/miniconda3/bin/activate" >> ~/.bashrc
RUN source ~/miniconda3/bin/activate && \
    conda init bash && \
    conda create -y -n llava python=3.10 && \
    conda activate llava
    #  && \
    # pip install --upgrade pip && \
    # pip install -e .

WORKDIR /opt/lava

# download pretrained model
RUN git clone https://huggingface.co/liuhaotian/llava-v1.5-13b

ENTRYPOINT ["bash", "start.sh"]
