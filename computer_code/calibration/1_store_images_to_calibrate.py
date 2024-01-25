import os
import cv2
import threading
import numpy as np
import urllib.request
from datetime import datetime

#################
# Description   #
#################
# This is a program to store images from both ESP32-CAMs 'simultaneously' for calibration.

# Note from the robot's perspective:
# AI-Thinker ESP32-CAM: Robot's right eye
# M5Stack Wide ESP32-CAM: Robot's left eye

#################
# Instructions  #
#################

# 1. Print a chessboard pattern and stick it on a flat surface.
#    It's recommended you take the chessboard from OpenCV's website,
#    as the number of inner corners are already specified (9x6 in 10x7 squares)
#    https://github.com/opencv/opencv/blob/4.x/doc/pattern.png
# 2. When you run this script, you should hold the chessboard in different positions
#    so that the cameras can capture it from different angles. You should see
#    the chessboard pattern in both cameras' frames (in full) before accepting the pair
#    (by pressing 's').

# You can experiment in your first attempt with various distances.
# If after calibration (in the next file) the corners are not detected well or the lines
# connecting them are not correct, you should remove the faulty images and re-calibrate.
# If not enough images are left, you should refill the folder capturing from a shorter distance.
# I saved ~40 image pairs to calibrate the cameras.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
USE_HOTSPOT = False

ip_left = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*"  # Left eye's IP, e.g. (192, 168, 1, 180).             ** Replace
ip_right = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*" # Right eye's IP, e.g. (192, 168, 1, 181).            ** Replace
esp32_right_image_url = f"http://{ip_right}/image.jpg"
esp32_left_image_url = f"http://{ip_left}/image.jpg"

save_path_right = "./images/right_eye"
save_path_left = "./images/left_eye"

frame_interval = 3  # Time to wait between frames in seconds. You have this much time to press 's'
num_images = 100  # Total number of image pairs to capture (of which some you may save)

# Function to handle the image fetching in a thread
def fetch_image(url, queue):
    """Fetch an image from the specified URL and put it in the queue."""
    try:
        resp = urllib.request.urlopen(url)
        img_np = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        queue.append(img)
    except urllib.error.URLError as e:
        print(f"Error fetching image from {url}: {e}")
        queue.append(None)

# Function to capture a pair of images and save them if you press 's'
def capture_stereo_images(url_left, url_right, save_path_left, save_path_right):
    """Capture a pair of images from the specified URLs and save them if you press 's'."""
    queue_left, queue_right = [], []

    # Start threads for image capture
    thread_left = threading.Thread(target=fetch_image, args=(url_left, queue_left))
    thread_right = threading.Thread(target=fetch_image, args=(url_right, queue_right))
    
    thread_left.start()
    thread_right.start()

    # Wait for both threads to finish
    thread_left.join()
    thread_right.join()

    # Retrieve images from the queues
    img_left, img_right = queue_left[0], queue_right[0]

    # Concatenate images side-by-side
    if img_left is not None and img_right is not None:
        combined_image = cv2.hconcat([img_right, img_left])
        cv2.imshow("Stereo Cameras", combined_image)
    else:
        print("One or both images are None.")
    
    key = cv2.waitKey(frame_interval * 1000)

    # Save images if you press 's'
    if key == ord('s'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_filename_left = os.path.join(save_path_left, f"stereo_image_{timestamp}.jpg")
        save_filename_right = os.path.join(save_path_right, f"stereo_image_{timestamp}.jpg")
        cv2.imwrite(save_filename_left, img_left)
        cv2.imwrite(save_filename_right, img_right)
        print(f"Saved {save_filename_left} and {save_filename_right}")
        return True
    return False

def main():
    # Ensure the save directories exist
    os.makedirs(save_path_left, exist_ok=True)
    os.makedirs(save_path_right, exist_ok=True)

    # Capture images
    for i in range(num_images):
        saved = capture_stereo_images(esp32_left_image_url, esp32_right_image_url, 
                                      save_path_left, save_path_right)
        if not saved:
            print(f"Pair {i} not saved. Capturing next pair.")
        else:
            print(f"Pair {i} saved. Capturing next pair.")

    cv2.destroyAllWindows()
    print("Stereo image capturing completed.")

if __name__ == "__main__":
    main()
