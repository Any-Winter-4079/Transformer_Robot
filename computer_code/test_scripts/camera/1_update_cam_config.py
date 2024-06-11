import cv2
import time
import requests
import numpy as np
import urllib.request

#################
# Description   #
#################
# This is a test program to update the camera configuration from the computer.
# Computer and ESP32 are connected to the same WiFi network (or hotspot).
# The available cameras on the robot are:
# - M5Stack Wide Camera
# - Ai-Thinker Camera
# Thus the decision to pick one or the other changes the ip variable,
# since every ESP32-CAM has a different IP (set in their .ino code).

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Notes         #
#################
# Lowering the clock frequency (from 20MHz to 8MHz max) makes the image clearer,
# which may improve processes such as camera calibration and image stitching.

# Make sure you don't see:
# Error 501: Not Implemented
# or that'll mean the camera config update didn't work (even if OpenCV still displays an image
# - it may not be of the desired size or quality).
# For example, I tend to see it for too low JPEG_QUALITY values (very high quality).

# If you lose the image stream, the camera may reset and hence lose the updated configuration
# (i.e. the camera will reinitialize with the default FRAME_SIZE and JPEG_QUALITY in the code).
# Because of that, when the stream is recovered, we have to update the configuration again.
# Some waiting time is advisable to give the camera breathing room to recover and reset.

# M5Stack Wide Camera

# | FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
# |-----------------|----------------|----------------|-----------------|-----------------|-----------------|
# | QVGA (320x240)  | Err            | 0.045          | 0.035           | 0.032           | 0.030           |
# | VGA (640x480)   | 0.141          | 0.112          | 0.077           | 0.074           | 0.067           |
# | SVGA (800x600)  | 0.177          | 0.126          | 0.113           | 0.075           | 0.067           |
# | XGA (1024x768)  | 0.365          | 0.282          | 0.197           | 0.153           | 0.152           |
# | SXGA (1280x1024)| 0.491          | 0.335          | 0.248           | 0.183           | 0.166           |
# | UXGA (1600x1200)| 0.618          | 0.409          | 0.300           | 0.222           | 0.191           |

# Ai-Thinker Camera

# | FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
# |-----------------|----------------|----------------|-----------------|-----------------|-----------------|
# | QVGA (320x240)  | Err            | 0.039          | 0.029           | 0.030           | 0.027           |
# | VGA (640x480)   | 0.139          | 0.118          | 0.074           | 0.075           | 0.068           |
# | SVGA (800x600)  | 0.143          | 0.111          | 0.107           | 0.067           | 0.067           |
# | XGA (1024x768)  | 0.286          | 0.269          | 0.182           | 0.148           | 0.150           |
# | SXGA (1280x1024)| 0.374          | 0.258          | 0.212           | 0.173           | 0.155           |
# | UXGA (1600x1200)| 0.503          | 0.307          | 0.218           | 0.221           | 0.194           |

#################
# Configuration #
#################
JPEG_QUALITY = 32 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_UXGA" # FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
USE_HOTSPOT = False
M5STACKWIDE_CAMERA = False
NUM_ITERATIONS = 1000

ip = "*.*.*.*" if M5STACKWIDE_CAMERA and USE_HOTSPOT else "*.*.*.*" if M5STACKWIDE_CAMERA else "*.*.*.*" if USE_HOTSPOT else "*.*.*.*"  #  ESP32-CAM IPs, e.g. (192, 168, 1, 181).            ** Replace **
esp32_config_url = f"http://{ip}/camera_config"
esp32_image_url = f"http://{ip}/image.jpg"

# Function to fetch an image with a timeout
def fetch_image_with_timeout(url, timeout=10.0):
    """Fetch an image from the specified URL with a timeout."""
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        img_np = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Timeout or error fetching image from {url}: {e}")
        return None
    
# Function to update the camera configuration
def update_camera_config(jpeg_quality, frame_size):
    """Send a request to update the camera configuration."""
    data = {'jpeg_quality': jpeg_quality, 'frame_size': frame_size}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(esp32_config_url, data=data, headers=headers)
        print(f"Response from ESP32: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending request: {e}")

def main():
    total_time = 0
    stream_to_recover = False
    stream_active = False
    update_camera_config(JPEG_QUALITY, FRAME_SIZE)

    for _ in range(NUM_ITERATIONS):

        if stream_to_recover and stream_active:
            print("Stream is being recovered.")
            update_camera_config(JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False
        
        fetch_start = time.time()
        img = fetch_image_with_timeout(esp32_image_url)
        fetch_end = time.time()

        if img is None:
            print(f"No image from {esp32_image_url}.")
            stream_to_recover = True
            # Wait for the camera to recover
            cv2.waitKey(1000)
            continue
        else:
            stream_active = True
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        total_time += (fetch_end - fetch_start)

    average_time = total_time / NUM_ITERATIONS
    print(f"\nAverage fetch time over {NUM_ITERATIONS} iterations: {average_time:.3f} seconds")

if __name__ == "__main__":
    main()
