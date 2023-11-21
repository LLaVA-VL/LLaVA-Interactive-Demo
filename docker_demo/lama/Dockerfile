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

WORKDIR /opt/lama

COPY --chown=appuser lama/conda_env.yml .
# COPY --chown=vscode lama/conda_env.yml .

RUN source ~/miniconda3/bin/activate && \
    conda env create -n lama -f conda_env.yml -y && \
    conda activate lama && \
    conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch -y

RUN source ~/miniconda3/bin/activate && \
    conda activate lama && \
    pip install torch==1.10.2+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
    pip install torchvision==0.11.3+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
    pip install flask && \
    pip install pytorch-lightning

# RUN git clone https://huggingface.co/smartywu/big-lama download && \
#     unzip -n -q download/big-lama.zip

ENTRYPOINT ["bash", "docker_demo/lama/start.sh"]
