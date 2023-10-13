echo "Cloning dependent repos..." 
git clone --single-branch https://github.com/wchen-github/GLIGEN.git
git clone --single-branch https://github.com/wchen-github/gradio.git
git clone --single-branch https://github.com/wchen-github/Segment-Everything-Everywhere-All-At-Once.git SEEM
git clone --single-branch https://github.com/wchen-github/LLaVA
git clone --single-branch https://github.com/advimman/lama.git	

echo "Creating environments and download pretrained models..."
cd LLaVA
conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip  # enable PEP 660 support
pip install -e .
#download pretrained model
git clone https://huggingface.co/liuhaotian/llava-v1.5-13b
cd ..

#setting up lama
cd lama
conda env create -f conda_env.yml
conda activate lama
conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch -y
#pip install pytorch-lightning==1.2.9
#download pretrained model
pip3 install wldhx.yadisk-direct
curl -L $(yadisk-direct https://disk.yandex.ru/d/ouP6l8VJ0HpMZg) -o big-lama.zip
unzip big-lama.zip

cd ..
echo "Done setting up."