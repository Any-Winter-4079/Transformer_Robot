import os
import time
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "input_images/arrow_left.png"

base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": """You are a physical robot tasked with following a blue lane on a brown floor. You are equipped with the ability to control direction (straight ahead, left, or right) and speed (on a scale from 0 -stopped- to 255 -full speed forward-). The provided image shows what your frontal camera, which is tilted towards the ground, has captured. This represents what is directly ahead of you, with the bottom of the image being closest to you.

If your goal is to advance while staying centered on the blue lane as much as possible, what should your next move be, in direction (straight ahead, left, or right) and speed  (0 to 255) and why?"""
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 100
}

for i in range(1):
    start_time = time.time()
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(f"Time taken: {time.time() - start_time}")
    print(response.json())
