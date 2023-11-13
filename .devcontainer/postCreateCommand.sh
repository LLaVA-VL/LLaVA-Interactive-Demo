git config --global safe.directory '*'
git config --global core.editor "code --wait"
git config --global pager.branch false

# Set AZCOPY concurrency to auto
echo "export AZCOPY_CONCURRENCY_VALUE=AUTO" >> ~/.zshrc
echo "export AZCOPY_CONCURRENCY_VALUE=AUTO" >> ~/.bashrc

# Add dotnet to PATH
echo 'export PATH="$PATH:$HOME/.dotnet"' >> ~/.zshrc
echo 'export PATH="$PATH:$HOME/.dotnet"' >> ~/.bashrc

# Activate conda by default
echo "source /home/vscode/miniconda3/bin/activate" >> ~/.zshrc
echo "source /home/vscode/miniconda3/bin/activate" >> ~/.bashrc

# Use llava_int environment by default
echo "conda activate llava_int" >> ~/.zshrc
echo "conda activate llava_int" >> ~/.bashrc

# Activate conda on current shell
source /home/vscode/miniconda3/bin/activate

# Create and activate llava_int environment
conda create -n llava_int -c conda-forge -c pytorch python=3.10.8 pytorch=2.0.1 -y
conda activate llava_int

# Install Nvidia Cuda Compiler
conda install -y -c nvidia cuda-compiler

pip install -r requirements.txt

source setup.sh

echo "postCreateCommand.sh COMPLETE!"
