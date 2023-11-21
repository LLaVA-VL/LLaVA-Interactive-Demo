# Use the nvidia/cuda image as the base image
# FROM mcr.microsoft.com/devcontainers/base:ubuntu-20.04
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

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

# Create the group with ID '500000513'
RUN groupadd -g 500000513 appgroup

# Add the user 'appuser' with the specified user ID and group ID
RUN useradd -u 516398317 -g 500000513 -ms /bin/bash appuser

USER appuser
# USER vscode

# Download and install miniconda
RUN cd /tmp && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    rm ./Miniconda3-latest-Linux-x86_64.sh

RUN echo "source ~/miniconda3/bin/activate" >> ~/.bashrc

WORKDIR /opt/llava

COPY --chown=appuser LLaVA .
# COPY --chown=vscode LLaVA .

RUN source ~/miniconda3/bin/activate && \
    conda init bash && \
    conda create -y -n llava python=3.10 && \
    conda activate llava

RUN source ~/miniconda3/bin/activate && \
    conda activate llava && \
    pip install --upgrade pip && \
    pip install -e .

# download pretrained model
# RUN git clone https://huggingface.co/liuhaotian/llava-v1.5-13b

ENTRYPOINT ["bash", "docker_demo/llava/start.sh"]
