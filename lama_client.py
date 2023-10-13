
import requests
import base64
from PIL import Image, ImageOps
import io
import json

# Define the URL of the REST API endpoint
url = "http://localhost:9171/api/v2/image"

with open("img_1.png", "rb") as image_file:
  encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
  print(type(encoded_string))
  print(encoded_string[0:500])

  image_bytes = base64.b64decode(encoded_string)
  image_stream = io.BytesIO(image_bytes)
  image = Image.open(image_stream)
  print(image.format_description)

with open("img_1_mask.png", "rb") as image_file:
  mask = Image.open(image_file)
  if (mask.mode != "L"):
    mask = mask.convert("L")
  mask = ImageOps.invert(mask)      
  mask.save("img_1_mask_neg.png")

with open("img_1_mask.png", "rb") as image_file:
  encoded_string_mask = base64.b64encode(image_file.read()).decode("utf-8")
  print(type(encoded_string_mask))

  image_bytes = base64.b64decode(encoded_string)
  image_stream = io.BytesIO(image_bytes)
  image = Image.open(image_stream)
  print(image.format_description)

# Create a POST request to the endpoint
headers = {"Content-Type": "application/json"}
data = {"image": encoded_string, "mask": encoded_string_mask}
response = requests.post(url, headers=headers, json=data)

# Check the status code of the response
if response.status_code == 200:
  # The request was successful
  print("Image sent successfully")
  image_data = response.content
  # Create a io.BytesIO object from the image data
  dataBytesIO = io.BytesIO(image_data)
  # Open the image using Image.open()
  image = Image.open(dataBytesIO)
  # You can now manipulate the image as you wish
  print(image.format_description)
  print(image.format)
  print(image.size)
  print(image.mode)
  image.save("test_image_copy.png")

else:
  # The request failed
  print("Error: HTTP status code {}".format(response.status_code))
  print(response.text)
