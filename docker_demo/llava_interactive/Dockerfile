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

WORKDIR /opt/llava_int

COPY --chown=appuser requirements.txt .
# COPY --chown=vscode requirements.txt .

RUN source ~/miniconda3/bin/activate && \
    conda create -n llava_int -c conda-forge -c pytorch python=3.10.8 pytorch=2.0.1 -y && \
    conda activate llava_int && \
    conda install -y -c nvidia cuda-compiler

RUN source ~/miniconda3/bin/activate && \
    conda activate llava_int && \
    pip install -r requirements.txt

ENTRYPOINT ["bash", "docker_demo/llava_interactive/start.sh"]
