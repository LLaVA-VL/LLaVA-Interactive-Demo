
# 🌋 LLaVA-Interactive

*An All-in-One Demo for Image Chat, Segmentation and Generation/Editing.*

[[Project Page](https://llava-vl.github.io/llava-interactive/)] [[Demo](https://llavainteractive.ngrok.app/)] [[Paper](https://arxiv.org/abs/2311.00571)]

<p align="center">
    <img src="https://github.com/LLaVA-VL/llava-interactive/blob/main/images/llava_interactive_logo.png" width="45%">
    <br>
</p>

# Install

Installing this project requires CUDA 11.7 or above. Follow the steps below:

```bash
git clone https://github.com/LLaVA-VL/LLaVA-Interactive-Demo.git
conda create -n llava_int -c conda-forge -c pytorch python=3.10.8 pytorch=2.0.1 -y
conda activate llava_int
cd LLaVA-Interactive-Demo
pip install -r requirements.txt
source setup.sh
```

# Run the demo

To run the demo, simply run the shell script.

```bash
source .env.export
./run_demo.sh
```

# Run the demo in Background

To run the demo, simply run the shell script.

```bash
nohup ./run_demo.sh > demo.log 2>&1 &
```

<p align="center">
    <img src="https://github.com/LLaVA-VL/llava-interactive/blob/main/images/llava_interactive_workflow.png" width="50%">
    <br>
</p>

# Serve the demo

```bash
az login

NGROK_AUTHTOKEN=$(az keyvault secret show --vault-name $KEYVAULT_RESOURCE_NAME -n $NGROK_SECRET_NAME --query "value" -o tsv)
echo "${NGROK_AUTHTOKEN:0:5}...${NGROK_AUTHTOKEN: -5}"

ngrok config add-authtoken $NGROK_AUTHTOKEN

ngrok start llavainteractive --config ./ngrok.yml,/home/vscode/.config/ngrok/ngrok.yml
```

## Run ngrok in background

```bash
nohup ngrok start llavainteractive --config ./ngrok.yml,/home/vscode/.config/ngrok/ngrok.yml > ngrok.log 2>&1 &
```
## Vew Ngrok Process

http://localhost:4040/status

## Viewing Running Background Processes

```bash
ps -ef --forest
```

```bash
ps -ef --forest e
```

### Example Output

```zsh
...
vscode     19000       1  0 Jan17 ?        SNl  146:04 ngrok start llavainteractive --config ./ngrok.yml,/home/vscode/.config/ngrok/ngrok.yml DOCKER_BUILDKIT=1 HOSTNAME=cf7954859b6f CONTENT_MODERATOR_NAME=lla
vscode     95922       1  0 Jan17 ?        SN     0:00 /bin/bash ./run_demo.sh DOCKER_BUILDKIT=1 HOSTNAME=cf7954859b6f CONTENT_MODERATOR_NAME=llava-int-contentmoderator HOME=/home/vscode EFFICIENT_AI_SUBSCRIP
vscode     96587   95922  0 Jan17 ?        SN     0:00  \_ /bin/bash ./run_demo.sh DOCKER_BUILDKIT=1 HOSTNAME=cf7954859b6f CONTENT_MODERATOR_NAME=llava-int-contentmoderator HOME=/home/vscode EFFICIENT_AI_SUBS
vscode     96595   96587 96 Jan17 ?        SNl  29249:06      \_ python llava_interactive.py --moderate input_text_guardlist input_text_aics input_text_aics_jailbreak input_image_aics output_text_guardlist ou
vscode     95948       1  0 Jan17 ?        SNl   34:45 python -m llava.serve.controller --host 0.0.0.0 --port 10000 SHELL=/bin/bash LSCOLORS=Gxfxcxdxbxegedabagacad USER_ZDOTDIR=/home/vscode COLORTERM=truecolo
vscode     95949       1  0 Jan17 ?        SNl   60:10 python -m llava.serve.model_worker --host 0.0.0.0 --controller http://localhost:10000 --port 40000 --worker http://localhost:40000 --model-path ./llava-v
vscode     96487       1  0 Jan17 ?        SN     0:02 python ../lama_server.py SHELL=/bin/bash LSCOLORS=Gxfxcxdxbxegedabagacad USER_ZDOTDIR=/home/vscode COLORTERM=truecolor LESS=-R TERM_PROGRAM_VERSION=1.85.
vscode   1947877   96487  8 19:07 ?        SNl    0:14  \_ /home/vscode/miniconda3/envs/lama/bin/python /workspaces/LLaVA-Interactive-Demo/lama_server.py SHELL=/bin/bash LSCOLORS=Gxfxcxdxbxegedabagacad USER_Z
...
```

```bash
ps --help a
```

### Kill Demo Process

```bash
pkill --signal 9 -f llava.serve.controller
pkill --signal 9 -f llava.serve.model_worker
pkill --signal 9 -f lama_server
pkill --signal 9 -f llava_interactive
pkill --signal 9 -f ngrok
```

# Citation

If you find LLaVA-Interactive useful for your research and applications, please cite using this BibTeX:
```bash
  @article{chen2023llava_interactive,
    author      = {Chen, Wei-Ge and Spiridonova, Irina and Yang, Jianwei and Gao, Jianfeng and Li, Chunyuan},
    title       = {LLaVA-Interactive: An All-in-One Demo for Image Chat, Segmentation, Generation and Editing},
    publisher   = {arXiv:2311.00571},
    year        = {2023}
  }
```

# Related Projects

- [LLaVA: Large Language and Vision Assistant](https://github.com/haotian-liu/LLaVA)
- [SEEM: Segment Everything Everywhere All at Once](https://github.com/UX-Decoder/Segment-Everything-Everywhere-All-At-Once)
- [GLIGEN: Open-Set Grounded Text-to-Image Generation](https://github.com/gligen/GLIGEN)

# Acknowledgement

- [LaMa](https://github.com/advimman/lama): A nice tool we use to fill the background holes in images.

# Terms of use

By using this service, users are required to agree to the following terms: The service is a research preview intended for non-commercial use only. It only provides limited safety measures and may generate offensive content. It must not be used for any illegal, harmful, violent, racist, or sexual purposes. The service may collect user dialogue data for future research. For an optimal experience, please use desktop computers for this demo, as mobile devices may compromise its quality.

# License

This project including LLaVA and SEEM are licensed under the Apache License. See the [LICENSE](LICENSE) file for more details. The GLIGEN project is licensed under the MIT License.

The service is a research preview intended for non-commercial use only, subject to the model [License](https://github.com/facebookresearch/llama/blob/main/MODEL_CARD.md) of LLaMA, [Terms of Use](https://openai.com/policies/terms-of-use) of the data generated by OpenAI, and [Privacy Practices](https://chrome.google.com/webstore/detail/sharegpt-share-your-chatg/daiacboceoaocpibfodeljbdfacokfjb) of ShareGPT. Please contact us if you find any potential violation.
