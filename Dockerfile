# Use the nvidia/cuda image as the base image
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04

# Download and install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
	bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
	rm Miniconda3-latest-Linux-x86_64.sh

# Add conda to PATH
ENV PATH /opt/conda/bin:$PATH

# Create a conda environment with numpy and pandas
RUN conda create -n myenv numpy pandas
RUN conda activate myenv
