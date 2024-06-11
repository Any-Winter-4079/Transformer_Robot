import os
import re
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
import mediapipe as mp
from ultralytics import YOLO
from deepface import DeepFace

#################
# Description   #
#################
# This is a program to continuously try to fetch a pair of images from the ESP32-CAMs and:
# Work with one or both images, depending on their availability.
# Detect faces and objects in the images.
# Recognize faces (if any are detected).
# Calculate the depth of objects (if any are detected and all images are available).

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# MPS Device    #
#################
# pip install ultralytics
# pip uninstall torch torchvision torchaudio
# pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu

# export PYTORCH_ENABLE_MPS_FALLBACK=1

#################
# yolov8n       #
#################
# For objects:
# Have yolov8n.pt file in the same folder as 1_calculate_depth_and_run_recognition.py
# Have coco.names file in the same folder as 1_calculate_depth_and_run_recognition.py

#################
# DeepFace      #
#################
# For face recognition:
# Have production_database in the same folder as 1_calculate_depth_and_run_recognition.py 

#################
# Mediapipe     #
#################
# For face detection:
# Nothing needed 

#################
# SGBM          #
#################
# For depth:
# Nothing needed

#################
# Rectification #
#################
# Have stereo_maps in STEREO_MAPS_DIR

#################
# Configuration #
#################
JPEG_QUALITY = 12 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA" # FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
USE_HOTSPOT = True
RIGHT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*" #  Right eye ESP32-CAM IP, e.g. (192, 168, 1, 180).               ** Replace **
LEFT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*"  #  Left eye ESP32-CAM IP, e.g. (192, 168, 1, 181).                ** Replace **
STREAM_TIMEOUT = 3 # seconds
# Stereo
STEREO_MAPS_DIR = '../undistortion_and_rectification/stereo_maps'
# Object depth
USE_IQR = True
LABELS = ["bottle"]
STEREO_BLOCK_SIZE = 11 # Must be odd
MIN_DISPARITY = 8
NUM_DISPARITIES = 5 * 16 # Must be non-zero, divisible by 16
SPECKLE_WINDOW_SIZE = 0
SPECKLE_RANGE = 2
MODE = cv2.STEREO_SGBM_MODE_HH
UNIQUENESS_RATIO = 0
PRE_FILTER_CAP = 0
DISP12MAX_DIFF = 32
# Face recognition
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
stereoMapL_x = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapL_x.npy'))
stereoMapL_y = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapL_y.npy'))
stereoMapR_x = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapR_x.npy'))
stereoMapR_y = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapR_y.npy'))
Q = np.load(os.path.join(STEREO_MAPS_DIR, 'Q.npy'))

stereo = cv2.StereoSGBM_create(minDisparity=MIN_DISPARITY,
                               numDisparities=NUM_DISPARITIES,
                               blockSize=STEREO_BLOCK_SIZE,
                               P1=8 * STEREO_BLOCK_SIZE**2,
                               P2=32 * STEREO_BLOCK_SIZE**2,
                               disp12MaxDiff=DISP12MAX_DIFF,
                               preFilterCap=PRE_FILTER_CAP,
                               uniquenessRatio=UNIQUENESS_RATIO,
                               speckleWindowSize=SPECKLE_WINDOW_SIZE,
                               speckleRange=SPECKLE_RANGE,
                               mode=MODE)

# Face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Object detection
object_detection_model = YOLO("yolov8n.pt")

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Stereo parameters trackbars
def on_min_disparity_change(val):
    global stereo
    stereo.setMinDisparity(val)

def on_num_disparities_change(val):
    global stereo
    stereo.setNumDisparities(max(16, (val // 16) * 16))

def on_block_size_change(val):
    global stereo
    stereo.setBlockSize(val if val % 2 == 1 else val + 1)

def on_speckle_window_size_change(val):
    global stereo
    stereo.setSpeckleWindowSize(val)

def on_speckle_range_change(val):
    global stereo
    stereo.setSpeckleRange(val)

def on_mode_change(val):
    global stereo
    stereo.setMode(cv2.STEREO_SGBM_MODE_HH if val == 0 else cv2.STEREO_SGBM_MODE_SGBM_3WAY)

def on_uniqueness_ratio_change(val):
    global stereo
    stereo.setUniquenessRatio(val)

def on_pre_filter_cap_change(val):
    global stereo
    stereo.setPreFilterCap(val)

def on_disp12max_diff_change(val):
    global stereo
    stereo.setDisp12MaxDiff(val)

cv2.namedWindow("Stereo depth")
cv2.createTrackbar("Min Disp.", "Stereo depth", MIN_DISPARITY, 32, on_min_disparity_change)
cv2.createTrackbar("Num Disp.", "Stereo depth", NUM_DISPARITIES, 16 * 10, on_num_disparities_change)
cv2.createTrackbar("Block Size", "Stereo depth", STEREO_BLOCK_SIZE, 13, on_block_size_change)
cv2.createTrackbar("Speckle Win", "Stereo depth", SPECKLE_WINDOW_SIZE, 200, on_speckle_window_size_change)
cv2.createTrackbar("Speckle Range", "Stereo depth", SPECKLE_RANGE, 100, on_speckle_range_change)
cv2.createTrackbar("Mode", "Stereo depth", 0, 1, on_mode_change)
cv2.createTrackbar("Uniq. Ratio", "Stereo depth", UNIQUENESS_RATIO, 60, on_uniqueness_ratio_change)
cv2.createTrackbar("Pre Filter Cap", "Stereo depth", PRE_FILTER_CAP, 100, on_pre_filter_cap_change)
cv2.createTrackbar("Disp12MaxDiff", "Stereo depth", DISP12MAX_DIFF, 60, on_disp12max_diff_change)

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
        response = requests.post(esp32_config_url, data=data, headers=headers)
        print(f"Response from ESP32: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending request: {e}")

# Function to process an image and return face centroid if a face is detected
def get_face_centroid(image):
    """Process the image and return the face centroid if a face is detected."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height
            centroid = (x + w / 2, y + h / 2)
            return centroid
    return None

# Function to process an image and return face bounding box if a face is detected
def get_face_bounding_box(image):
    """Process the image and return the face bounding box if a face is detected."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height
            height, width, _ = image.shape
            x, y, w, h = int(x * width), int(y * height), int(w * width), int(h * height)
            return (x, y, w, h)
    return None

# Function to process an image and return object bounding boxes if objects are detected
def get_object_bounding_boxes(image, label_filter=None):
    """Process the image and return the object bounding boxes and labels IF objects are detected."""
    results = object_detection_model(image, device="mps")
    result = results[0]
    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    class_ids = np.array(result.boxes.cls.cpu(), dtype="int")
    filtered_bboxes = []
    filtered_labels = []
    for cls, bbox in zip(class_ids, bboxes):
        if label_filter is None or classes[cls] in label_filter:
            (x, y, x2, y2) = bbox
            filtered_bboxes.append((x, y, x2 - x, y2 - y))
            filtered_labels.append(classes[cls])
    return filtered_bboxes, filtered_labels

# Function to calculate the average depth within a bounding box using IQR
def calculate_average_depth(points_3D, bbox, use_iqr=True):
    """Calculate the average depth within a bounding box using either all pixels or the interquartile range."""
    x, y, w, h = bbox
    face_region = points_3D[y:y+h, x:x+w]
    valid_depths = face_region[:, :, 2]
    valid_depths = valid_depths[np.isfinite(valid_depths)]
    if valid_depths.size == 0:
        return None
    if use_iqr:
        q1 = np.percentile(valid_depths, 25)
        q3 = np.percentile(valid_depths, 75)
        iqr_depths = valid_depths[(valid_depths >= q1) & (valid_depths <= q3)]
        if iqr_depths.size == 0:
            return None
        average_depth = np.mean(iqr_depths)
    else:
        average_depth = np.mean(valid_depths)
    return average_depth

# Function to capture a pair of images
def get_stereo_images(url_left, url_right):
    """Get a pair of images from the specified URLs."""
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

# Function to rectify images
def rectify_images(img_left, img_right):
    """Rectify the images using the stereo rectification maps."""
    img_left_rectified = cv2.remap(img_left, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
    img_right_rectified = cv2.remap(img_right, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
    return img_left_rectified, img_right_rectified

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

# Function to calculate depth maps
def calculate_depth_maps(stereo, left_img_rectified, right_img_rectified):
    """Calculate the disparity map and 3D points from the rectified images."""
    disparity = stereo.compute(left_img_rectified, right_img_rectified)
    disp_norm = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    points_3D = cv2.reprojectImageTo3D(disparity, Q)
    return disp_norm, points_3D

def main():
    stream_to_recover = False
    stream_active = False

    # Update camera configurations
    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    # Build face recognition model
    DeepFace.build_model(MODEL)

    while True:
        # Check if stream needs to be recovered
        if stream_to_recover and stream_active:
            print("Stream is being recovered.")
            update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
            update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False

        # Fetch
        img_left, img_right = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        # Check if both images are None
        if img_left is None and img_right is None:
            print("Both images are None.")
            stream_to_recover = True
            cv2.waitKey(500)
            continue
        
        # Rectify
        if img_left is not None:
            stream_active = True
            img_left_rectified = rectify_left_image(img_left)
        if img_right is not None:
            stream_active = True
            img_right_rectified = rectify_right_image(img_right)

        # Detect face and objects in the left image
        if img_left is not None:
            left_face_bbox = get_face_bounding_box(img_left_rectified)
            left_object_bboxes, left_object_labels = get_object_bounding_boxes(img_left_rectified, label_filter=LABELS)
        
        # Detect face and objects in the right image
        if img_right is not None:
            right_face_bbox = get_face_bounding_box(img_right_rectified)
            right_object_bboxes, right_object_labels = get_object_bounding_boxes(img_right_rectified, label_filter=LABELS)

        # Check if only one image is None
        img_rectified_if_single = None
        img_face_bbox_if_single = None
        img_object_bboxes_if_single = None
        img_object_labels_if_single = None
        if img_left is None and img_right is not None:
            img_rectified_if_single = img_right
            img_face_bbox_if_single = right_face_bbox
            img_object_bboxes_if_single = right_object_bboxes
            img_object_labels_if_single = right_object_labels
        elif img_left is not None and img_right is None:
            img_rectified_if_single = img_left
            img_face_bbox_if_single = left_face_bbox
            img_object_bboxes_if_single = left_object_bboxes
            img_object_labels_if_single = left_object_labels

        # If both images are available
        if img_left is not None and img_right is not None:
            
            # And face and/or objects exist
            if (left_face_bbox is not None and right_face_bbox is not None) or \
                (len(left_object_bboxes) > 0 and len(right_object_bboxes) > 0):

                # For objects, put bounding boxes, labels, and add depth
                disp_norm, points_3D = calculate_depth_maps(stereo, img_left_rectified, img_right_rectified)

                # If face, put bounding box and perform recognition
                if left_face_bbox is not None:
                    x, y, w, h = left_face_bbox
                    result = recognize_face(img_left_rectified)
                    if result is not None:
                        draw_boxes_and_labels(img_left_rectified, result)
                    else:
                        cv2.rectangle(img_left_rectified, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                for bbox, label in zip(left_object_bboxes, left_object_labels):
                    x, y, w, h = bbox
                    cv2.rectangle(disp_norm, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.putText(disp_norm, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    cv2.rectangle(img_left_rectified, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img_left_rectified, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    average_object_depth = calculate_average_depth(points_3D, bbox, use_iqr=USE_IQR)
                    if average_object_depth is not None:
                        cv2.putText(disp_norm, f"Depth: {average_object_depth:.2f}", (x, y + h + 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                        print(f"{label} detected. Average {label} depth: {average_object_depth:.2f}")

                # Displaying both the depth and original (rectified) image
                disp_norm_color = cv2.cvtColor(disp_norm, cv2.COLOR_GRAY2BGR)
                combined = np.concatenate((disp_norm_color, img_left_rectified), axis=1)
                cv2.imshow("Stereo depth", combined)
        
        # Or, if only one is
        elif img_rectified_if_single is not None:
            
            # If face, put bounding box and perform recognition
            if img_face_bbox_if_single is not None:
                x, y, w, h = img_face_bbox_if_single
                result = recognize_face(img_rectified_if_single)
                if result is not None:
                    draw_boxes_and_labels(img_rectified_if_single, result)
                else:
                    cv2.rectangle(img_rectified_if_single, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # For objects, put bounding boxes, labels, without depth
            for bbox, label in zip(img_object_bboxes_if_single, img_object_labels_if_single):
                x, y, w, h = bbox
                cv2.rectangle(img_rectified_if_single, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img_rectified_if_single, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # And display the original (rectified) image
            cv2.imshow("Stereo depth", img_rectified_if_single)

        # Breaking the loop on 'q' press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
    cv2.destroyAllWindows()
