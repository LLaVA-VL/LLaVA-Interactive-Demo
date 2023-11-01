
# 🌋 LLaVA-Interactive

*An All-in-One Demo for Image Chat, Segmentation and Generation/Editing.*

[[Project Page](https://llava-vl.github.io/llava-interactive/)] [[Demo](https://6dd3-20-163-117-69.ngrok-free.app/)]

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
./run_demo.sh
```

<p align="center">
    <img src="https://github.com/LLaVA-VL/llava-interactive/blob/main/images/llava_interactive_workflow.png" width="50%"> 
    <br>
</p>


# Citation

If you find LLaVA-Interactive useful for your research and applications, please cite using this BibTeX:

  @article{chen2023llava_interactive,
    author      = {Chen, Wei-Ge and Spiridonova, Irina and Yang, Jianwei and Gao, Jianfeng and Li, Chunyuan},
    title       = {LLaVA-Interactive: An All-in-One Demo for Image Chat, Segmentation, Generation and Editing},
    publisher   = {https://llava-vl.github.io/llava-interactive},
    year        = {2023}
  }
  
# Related Projects

- [LLaVA: Large Language and Vision Assistant](https://github.com/haotian-liu/LLaVA)
- [SEEM: Segment Everything Everywhere All at Once](https://github.com/UX-Decoder/Segment-Everything-Everywhere-All-At-Once)
- [GLIGEN: Open-Set Grounded Text-to-Image Generation](https://github.com/gligen/GLIGEN)

# Acknowledgement

- [LaMa](https://github.com/advimman/lama): A nice tool we use to fill the background holes in images.

# License
This project including LLaVA and SEEM are licensed under the Apache License. See the [LICENSE](LICENSE) file for more details. The GLIGEN project is licensed under the MIT License.
