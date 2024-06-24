import os
import time
import base64
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv("CLAUDE_API_KEY")

# "claude-3-opus-20240229"
# "claude-3-sonnet-20240229"
# "claude-3-haiku-20240307"
# "claude-3-5-sonnet-20240620"
client = Anthropic(api_key=api_key)
MODEL_NAME = "claude-3-5-sonnet-20240620"

with open("input_images/arrow_left.png", "rb") as image_file:
    binary_data = image_file.read()
    base_64_encoded_data = base64.b64encode(binary_data)
    base64_string = base_64_encoded_data.decode('utf-8')


message_list = [
    {
        "role": 'user',
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_string}},
            {"type": "text", "text": """You are a physical robot tasked with following a blue lane on a brown floor. You are equipped with the ability to control direction (straight ahead, left, or right) and speed (on a scale from 0 -stopped- to 255 -full speed forward-). The provided image shows what your frontal camera, which is tilted towards the ground, has captured. This represents what is directly ahead of you, with the bottom of the image being closest to you.

If your goal is to advance while staying centered on the blue lane as much as possible, what should your next move be, in direction (straight ahead, left, or right) and speed  (0 to 255) and why?"""}
        ]
    }
]

for i in range(1):
    start_time = time.time()
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=100,
        messages=message_list
    )
    print(f"Time taken: {time.time() - start_time}")
    print(response.json())
