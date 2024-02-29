import os
import re
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
from deepface import DeepFace

#################
# Description   #
#################
# This is a script to perform face recognition on the ESP32-CAM images using the DeepFace library.

#################
# Instructions  #
#################
# Create a production_database folder and place some images from people you want to recognize.
# I placed 13 images of Tom Cruise and 13 images of myself.
# All images were resized to 512x512, although the frames come at 640x480.
# The structure should look like this:
# production_database
# ├── Tom_Cruise
# │   ├── Tom_Cruise_0001.jpg
# │   ├── Tom_Cruise_0002.jpg
# ├── Your_Name
# │   ├── Your_Name_0001.jpg
# │   ├── Your_Name_0002.jpg
# ...
# 3_run_face_recognition.py

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Notes         #
#################
# test_image_path can be a numpy array in DeepFace. So we don't need to save the image to disk.

#################
# Configuration #
#################
JPEG_QUALITY = 12 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA" # FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
USE_HOTSPOT = False
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
STREAM_TIMEOUT = 3 # seconds
CONFIG_TIMEOUT = 5 # seconds

DATABASE_PATH = "production_database"
DISTANCE_METRIC = "cosine" # cosine, euclidean, euclidean_l2
BACKEND = "fastmtcnn" # opencv, ssd, mtcnn, retinaface, mediapipe, yolov8, yunet, fastmtcnn
MODEL = "VGG-Face" # VGG-Face, Facenet, Facenet512, OpenFace, DeepID, ArcFace
THRESHOLD = 0.625 # (distances < this threshold will be returned from the find function.
# In other words, set how close the match should be. Lower values risk no matches)
# Note different metrics require different thresholds
# The defaults are:
# | Model       | Cosine | Euclidean | Euclidean L2 |
# |-------------|--------|-----------|--------------|
# | VGG-Face    | 0.68   | 1.17      | 1.17         |
# | Facenet     | 0.40   | 10        | 0.80         |
# | Facenet512  | 0.30   | 23.56     | 1.04         |
# | ArcFace     | 0.68   | 4.15      | 1.13         |
# | Dlib        | 0.07   | 0.6       | 0.4          |
# | SFace       | 0.593  | 10.734    | 1.055        |
# | OpenFace    | 0.10   | 0.55      | 0.55         |
# | DeepFace    | 0.23   | 64        | 0.64         |
# | DeepID      | 0.015  | 45        | 0.17         |

# For my case: 0.625, cosine, fastmtcnn, and VGG-Face worked well but you should experiment with different combinations.

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

# Function to draw boxes and labels
def draw_boxes_and_labels(img_rectified, unique_individuals):
    """Draw boxes and labels around the faces."""
    for person_name, info in unique_individuals.items():
        x, y, w, h = info['source_x'], info['source_y'], info['source_w'], info['source_h']
        identity = person_name
        identity = re.sub(r'_\d+$', '', identity)
        identity = identity.replace('_', ' ')
        cv2.rectangle(img_rectified, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img_rectified, identity, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# Function to get unique individuals
def get_top_predictions(dfs_list):
    """Extract the top prediction for each person from the list of dataframes."""
    top_predictions = []
    for df in dfs_list:
        if len(df) > 0:
            top_prediction = df.iloc[0]
            top_predictions.append(top_prediction)
    return top_predictions

# Function to get unique individuals
def process_predictions(top_predictions):
    """Process and extract unique individuals from top predictions."""
    unique_individuals = {}
    for prediction in top_predictions:
        identity_path = prediction['identity'].replace(DATABASE_PATH + '/', '').split('/')
        person_name = identity_path[0]
        if person_name not in unique_individuals:
            unique_individuals[person_name] = prediction
    return unique_individuals

# Function to recognize a face in an image using the DeepFace library
def recognize_face(test_image_path):
      """Recognize a face in an image using the DeepFace library."""
      try:
        dfs = DeepFace.find(
           img_path=test_image_path,
           db_path=DATABASE_PATH,
           model_name=MODEL,
           detector_backend=BACKEND,
           distance_metric=DISTANCE_METRIC,
           enforce_detection=False,
           threshold=THRESHOLD)
        top_predictions = get_top_predictions(dfs)
        unique_individuals = process_predictions(top_predictions)
        return unique_individuals
      except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {MODEL} and backend {BACKEND}: {e}\n")

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

    thread_left = threading.Thread(target=fetch_image_with_timeout, args=(url_left, queue_left))
    thread_right = threading.Thread(target=fetch_image_with_timeout, args=(url_right, queue_right))
    
    thread_left.start()
    thread_right.start()

    thread_left.join()
    thread_right.join()

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
    total_face_rec_time = 0
    stream_to_recover = False
    stream_active = False
    face_rec_iterations = 0

    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    DeepFace.build_model(MODEL)

    while True:
        if stream_to_recover and stream_active:
            print("Stream recovered.")
            update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
            update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False
        
        img_right, img_left = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        if img_right is not None:
            img_rectified = rectify_right_image(img_right)
        elif img_left is not None:
            img_rectified = rectify_left_image(img_left)
        else:
            print("Both images are None.")
            stream_to_recover = True
            cv2.waitKey(2000) # Wait for the camera to recover
            continue

        stream_active = True

        face_rec_start = time.time()
        result = recognize_face(img_rectified)
        face_rec_end = time.time()
        face_rec_iterations += 1
        total_face_rec_time += (face_rec_end - face_rec_start)
        if result is not None:
            draw_boxes_and_labels(img_rectified, result)
        cv2.imshow("Stereo face_rec", img_rectified)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    average_face_rec_time = total_face_rec_time / face_rec_iterations
    print(f"Average face_rec calculation time over {face_rec_iterations} iterations: {average_face_rec_time:.3f} seconds")

if __name__ == "__main__":
    main()
