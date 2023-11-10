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
RUN source ~/miniconda3/bin/activate
    # Lama source isn't mounded so can't run install?
#     conda env create -n lama -f conda_env.yml -y && \
#     conda activate lama && \
#     conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch -y

# RUN pip install torch==1.10.2+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
#     pip install torchvision==0.11.3+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html && \
#     pip install flask && \
#     pip install pytorch-lightning

# RUN git clone https://huggingface.co/smartywu/big-lama download && \
#     unzip -n -q download/big-lama.zip

WORKDIR /opt/lama

ENTRYPOINT ["bash"]
# ENTRYPOINT ["bash", "start.sh"]
