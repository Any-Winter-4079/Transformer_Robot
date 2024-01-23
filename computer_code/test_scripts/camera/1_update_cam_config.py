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
# Configuration #
#################
JPEG_QUALITY = 12 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA" # FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
USE_HOTSPOT = False
M5STACKWIDE_CAMERA = False
ITERATIONS = 200

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
    update_camera_config(JPEG_QUALITY, FRAME_SIZE)

    for _ in range(ITERATIONS):
        
        fetch_start = time.time()
        img = fetch_image_with_timeout(esp32_image_url)
        fetch_end = time.time()

        if img is None:
            print(f"No image from {esp32_image_url}.")
            continue
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        total_time += (fetch_end - fetch_start)

    average_time = total_time / ITERATIONS
    print(f"\nAverage fetch time over {ITERATIONS} iterations: {average_time:.2f} seconds")

if __name__ == "__main__":
    main()
