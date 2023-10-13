
from flask import Flask, jsonify, send_file, request
import base64
from PIL import Image, ImageOps
import io

import hydra
from omegaconf import DictConfig
from lama.bin.predict_web_server import main as lama_prediction

import os
import yaml
from omegaconf import OmegaConf

cwd = os.getcwd()
print(cwd)

config_path = os.path.join(cwd, "configs/prediction/default.yaml")
with open(config_path, 'r') as f:
  config = OmegaConf.create(yaml.safe_load(f))

config.model.path = os.path.join(cwd, "big-lama")
config.indir = os.path.join(cwd, "web_server_input")
config.outdir = os.path.join(cwd, "web_server_output")
config.refine = False

app = Flask(__name__)

@app.route("/api/v2/image", methods=["GET", "POST"])
def echo_image():
  # Get the image data from the request body
  json_dict = request.get_json()
  print(type(json_dict))
  # Get the value of the "image" key, which is the base64 encoded image data
  base64_image_data = json_dict["image"]
  #print(base64_image_data[0:500])

  image_bytes = base64.b64decode(base64_image_data)
  image_stream = io.BytesIO(image_bytes)
  image = Image.open(image_stream)
  print(image.format_description)
  if not os.path.exists("web_server_input"):
    os.makedirs("web_server_input")
  image.save("web_server_input/server.png")

  base64_mask_data = json_dict["mask"]  
  image_bytes = base64.b64decode(base64_mask_data)
  image_stream = io.BytesIO(image_bytes)
  mask = Image.open(image_stream)
  print(mask.format_description)
  print(mask.format)
  print(mask.size)
  print(mask.mode)
  if (mask.mode != "L"):
    mask = mask.convert("L")
  if not os.path.exists("web_server_input"):
    os.makedirs("web_server_input")
  mask.save("web_server_input/server_mask.png")

  # Apply the mask to the image
  # Create a new transparent image with the same size and mode as the image
  transparent = Image.new(image.mode, image.size, (0, 0, 0, 0))
  # Composite the image and the transparent image using the mask
  masked_image = Image.composite(image, transparent, mask)
  masked_image.save("server_masked_image.png")  

  # Convert the masked image to bytes and create a new stream
  masked_image_stream = io.BytesIO()
  masked_image.save(masked_image_stream, format='PNG')
  masked_image_stream.seek(0)

  lama_prediction(config)

  with open("web_server_output/server_mask.png", "rb") as image_file:
    image_bytes = image_file.read() 
    image_inpainted_stream = io.BytesIO(image_bytes)
    print(image.format_description)  
  image_inpainted_stream.seek(0)

  return send_file(image_inpainted_stream, mimetype="image/png")

if __name__ == "__main__":
  app.run(debug=True, port=9171)

