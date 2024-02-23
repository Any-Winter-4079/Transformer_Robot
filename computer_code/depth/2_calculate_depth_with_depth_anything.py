import os
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
from depth_anything.run import get_depth
from depth_anything.depth_anything.dpt import DepthAnything

#################
# Description   #
#################
# This is a program to continuously calculate the depth map from the right (or left if the right is not available) ESP32-CAM.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Instructions  #
#################
# Clone the Depth Anything repository (inside the 'depth' folder) and rename it to depth_anything.
# # https://github.com/LiheYoung/Depth-Anything
# Replace run.py and dpt.py (inside a second depth_anything folder) with the provided files.
# The structure should look like this:
# depth
# ├── depth_anything
# │   ├── depth_anything
# │   │   ├── dpt.py
# │   └── run.py
# ├── 2_calculate_depth_with_depth_anything.py
# Remember to install the requirements from the Depth Anything repository (requirements.txt)

#################
# Performance  #
#################
# M1 Max 64 GB RAM: Average depth calculation time over 174 iterations: 0.099 seconds

#################
# Improvements  #
#################
# Note we wait for both frames to arrive but we only calculate the depth map of one of them.
# While there is a timeout if one of the frames is not received, to continue using the other
# camera, we could also only take the first received frame without waiting for the second one,
# which will either potentially return an unused frame or will timeout. Waiting however
# does allow for the calculation of the depth map of both frames in the future.

#################
# Configuration #
#################
JPEG_QUALITY = 12 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA" # FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
USE_HOTSPOT = False
RIGHT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*" #  Right eye ESP32-CAM IP, e.g. (192, 168, 1, 180).               ** Replace **
LEFT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*"  #  Left eye ESP32-CAM IP, e.g. (192, 168, 1, 181).                ** Replace **
STREAM_TIMEOUT = 3 # seconds
CONFIG_TIMEOUT = 5 # seconds

# Cameras
esp32_right_image_url = f"http://{RIGHT_EYE_IP}/image.jpg"
esp32_left_image_url = f"http://{LEFT_EYE_IP}/image.jpg"
esp32_left_config_url = f"http://{LEFT_EYE_IP}/camera_config"
esp32_right_config_url = f"http://{RIGHT_EYE_IP}/camera_config"

# Stereo
stereo_maps_dir = '../undistortion_and_rectification/stereo_maps'
stereoMapL_x = np.load(os.path.join(stereo_maps_dir, 'stereoMapL_x.npy'))
stereoMapL_y = np.load(os.path.join(stereo_maps_dir, 'stereoMapL_y.npy'))
stereoMapR_x = np.load(os.path.join(stereo_maps_dir, 'stereoMapR_x.npy'))
stereoMapR_y = np.load(os.path.join(stereo_maps_dir, 'stereoMapR_y.npy'))
Q = np.load(os.path.join(stereo_maps_dir, 'Q.npy'))

# Depth Anything
encoder = 'vits' # can also be 'vitb' or 'vitl'
depth_anything = DepthAnything.from_pretrained('LiheYoung/depth_anything_{:}14'.format(encoder))

# Function to fetch an image with a timeout
def fetch_image_with_timeout(url, queue, timeout=STREAM_TIMEOUT):
    """Fetch an image from the specified URL with a timeout."""
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        img_np = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        queue.append(img)
    except Exception as e:
        print(f"Timeout or error fetching image from {url}: {e}")
        queue.append(None)

# Function to update the camera configuration
def update_camera_config(esp32_config_url, jpeg_quality, frame_size):
    """Send a request to update the camera configuration."""
    data = {'jpeg_quality': jpeg_quality, 'frame_size': frame_size}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(esp32_config_url, data=data, headers=headers, timeout=CONFIG_TIMEOUT)
        print(f"Response from ESP32: {response.text}")
        return True
    except requests.RequestException as e:
        print(f"Error sending request: {e}")
        return False

# Function to capture a pair of images
def get_stereo_images(url_left, url_right):
    """Get a pair of images from the specified URLs"""
    queue_left, queue_right = [], []

    # Start threads for image capture
    thread_left = threading.Thread(target=fetch_image_with_timeout, args=(url_left, queue_left))
    thread_right = threading.Thread(target=fetch_image_with_timeout, args=(url_right, queue_right))
    
    thread_left.start()
    thread_right.start()

    # Wait for both threads to finish
    thread_left.join()
    thread_right.join()

    # Retrieve images from the queues
    img_left = queue_left[0]
    img_right = queue_right[0]

    return img_left, img_right

# Function to rectify left image
def rectify_left_image(image):
    """Rectify the left image using the stereo rectification maps."""
    image_rectified = cv2.remap(image, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
    return image_rectified

# Function to rectify right image
def rectify_right_image(image):
    """Rectify the right image using the stereo rectification maps."""
    image_rectified = cv2.remap(image, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
    return image_rectified

def main():
    total_depth_time = 0
    stream_to_recover = False
    stream_active = False
    depth_iterations = 0
    # Update the camera configurations
    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    while True:
        if stream_to_recover and stream_active:
            print("Stream recovered.")
            update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
            update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False
        
        # Fetch images
        img_right, img_left = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        if img_right is not None:
            img_rectified = rectify_right_image(img_right)
        elif img_left is not None:
            img_rectified = rectify_left_image(img_left)
        else:
            print("Both images are None.")
            stream_to_recover = True
            # Wait for the camera to recover
            cv2.waitKey(1000)
            continue

        stream_active = True

        # Get depth
        depth_start = time.time()
        depth = get_depth(img_rectified)
        depth_end = time.time()
        depth_iterations += 1
        total_depth_time += (depth_end - depth_start)
        # Show the depth map
        cv2.imshow("Stereo depth", depth)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break
    
    average_depth_time = total_depth_time / depth_iterations
    print(f"Average depth calculation time over {depth_iterations} iterations: {average_depth_time:.3f} seconds")

if __name__ == "__main__":
    main()
