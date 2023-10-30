echo "Cloning dependent repos..."
git clone --single-branch https://github.com/wchen-github/GLIGEN.git
git clone --single-branch https://github.com/wchen-github/Segment-Everything-Everywhere-All-At-Once.git SEEM
git clone --single-branch https://github.com/wchen-github/LLaVA
git clone --single-branch https://github.com/advimman/lama.git

echo "Creating environments and download pretrained models..."

cd LLaVA
conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip # enable PEP 660 support
pip install -e .
#download pretrained model
git clone https://huggingface.co/liuhaotian/llava-v1.5-13b
cd ..

#setting up lama
cd lama
conda env create --name lama -f conda_env.yml -y
conda activate lama
conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch -y
pip install torch==1.10.2+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html
pip install torchvision==0.11.3+cu113 --find-links https://download.pytorch.org/whl/cu113/torch_stable.html
pip install flask
pip install pytorch-lightning
#download pretrained model
git clone https://huggingface.co/smartywu/big-lama download
unzip download/big-lama.zip

conda deactivate
cd ..
echo "Done setting up."
