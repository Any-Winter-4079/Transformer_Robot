import os
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
import mediapipe as mp

#################
# Description   #
#################
# This is a program to continuously calculate the depth map from a pair of stereo images, IF a face is detected.

#################
# Customization #
#################
# A trackbar window is created to adjust the stereo parameters in real-time.
# You can replace the face detection function (get_face_centroid) with a
# completely different oject detection function. Or, you can remove the
# face detection and calculate the depth map for every pair of images.

#################
# Depth value   #
#################
# The depth value of the interesting object can be calculated using the 2 centroids as points
# from where to retrieve the depth value. Or an average over more points could be used.

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
RIGHT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*" #  Right eye ESP32-CAM IP, e.g. (192, 168, 1, 180).               ** Replace **
LEFT_EYE_IP = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*"  #  Left eye ESP32-CAM IP, e.g. (192, 168, 1, 181).                ** Replace **
STREAM_TIMEOUT = 3 # seconds
STEREO_BLOCK_SIZE = 11 # Must be odd
MIN_DISPARITY = 0
NUM_DISPARITIES = 5 * 16 # Must be non-zero, divisible by 16
SPECKLE_WINDOW_SIZE = 0
SPECKLE_RANGE = 2
MODE = cv2.STEREO_SGBM_MODE_HH
UNIQUENESS_RATIO = 0
PRE_FILTER_CAP = 0
DISP12MAX_DIFF = 32

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

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

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

# Function to rectify images
def rectify_images(img_left, img_right):
    """Rectify the images using the stereo rectification maps."""
    img_left_rectified = cv2.remap(img_left, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
    img_right_rectified = cv2.remap(img_right, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
    return img_left_rectified, img_right_rectified

# Function to calculate depth maps
def calculate_depth_maps(stereo, left_img_rectified, right_img_rectified):
    """Calculate the disparity map and 3D points from the rectified images."""
    # Calculate disparity map
    disparity = stereo.compute(left_img_rectified, right_img_rectified)
    
    # Normalize the disparity map (for visualization)
    disp_norm = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Reproject points to 3D
    points_3D = cv2.reprojectImageTo3D(disparity, Q)
    
    # Return the normalized disparity map and 3D points
    return disp_norm, points_3D

def main():
    total_face_time = 0
    total_depth_time = 0
    stream_to_recover = False
    stream_active = False
    face_iterations = 0
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
        img_left, img_right = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        if img_left is not None and img_right is not None:
            stream_active = True

            # Rectify images
            img_left_rectified, img_right_rectified = rectify_images(img_left, img_right)

            # Concatenate images side-by-side
            combined = np.concatenate((img_left_rectified, img_right_rectified), axis=1)
            # Show the rectified images
            # cv2.imshow("Stereo frames (rectified)", combined)
            # if cv2.waitKey(5) & 0xFF == ord('q'):
            #     break
            
            # Detect face centroids
            face_start = time.time()
            left_centroid = get_face_centroid(img_left_rectified)
            right_centroid = get_face_centroid(img_right_rectified)
            face_end = time.time()
            face_iterations += 1
            total_face_time += (face_end - face_start)

            # Get depth
            if left_centroid is not None and right_centroid is not None:
                depth_start = time.time()
                disp_norm, points_3D = calculate_depth_maps(stereo, img_left_rectified, img_right_rectified)
                depth_end = time.time()
                depth_iterations += 1
                total_depth_time += (depth_end - depth_start)
                # Show the depth map
                cv2.imshow("Stereo depth", disp_norm)
                if cv2.waitKey(50) & 0xFF == ord('q'):
                    break

        else:
            print("One or both images are None.")
            stream_to_recover = True
            # Wait for the camera to recover
            cv2.waitKey(1000)
            continue

    average_face_time = total_face_time / face_iterations
    average_depth_time = total_depth_time / depth_iterations
    print(f"\nAverage face centroid calculation time over {face_iterations} iterations: {average_face_time:.3f} seconds")
    print(f"Average depth calculation time over {depth_iterations} iterations: {average_depth_time:.3f} seconds")

if __name__ == "__main__":
    main()
