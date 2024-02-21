import os
import cv2
import glob
import numpy as np

#################
# Description   #
#################
# This is a program to correct the fisheye distortion and rectify the images. Additionally,
# we save the stereo rectification maps for efficient reuse.
# - Undistortion corrects the lens distortion (the curvature of the images)
# - Rectification corrects the perspective distortion (alings points horizontally)

# We are using 2 OV2640, which have fisheye lenses, because of their 7.5cm cables,
# which allows us to pass the cable through the eye and plug it into the ESP32-CAM.
# If you are using say a pinhole camera, you will need to remove .fisheye from the functions.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
# You can change these paths to undistort and rectify other images
LEFT_EYE_IMAGES_DIR = '../calibration/images/left_eye'
RIGHT_EYE_IMAGES_DIR = '../calibration/images/right_eye'
OUTPUT_DIR = './images/undistorted_and_rectified_calibration_images'
STEREO_MAPS_DIR = './stereo_maps'

# Load calibration parameters
camera_matrix_left = np.load('../calibration/parameters/camera_matrix_left_eye.npy')
dist_coeffs_left = np.load('../calibration/parameters/distortion_coeffs_left_eye.npy')
camera_matrix_right = np.load('../calibration/parameters/camera_matrix_right_eye.npy')
dist_coeffs_right = np.load('../calibration/parameters/distortion_coeffs_right_eye.npy')
R = np.load('../calibration/parameters/rotation_matrix.npy')
T = np.load('../calibration/parameters/translation_vector.npy')

# Function to perform stereo rectification and map initialization
def initialize_stereo_rectification(image_size, camera_matrix_left, dist_coeffs_left, camera_matrix_right, dist_coeffs_right, R, T):
    """Perform stereo rectification and initialize the stereo rectification maps."""
    flags = cv2.CALIB_ZERO_DISPARITY
    R1, R2, P1, P2, Q = cv2.fisheye.stereoRectify(camera_matrix_left, dist_coeffs_left, camera_matrix_right, dist_coeffs_right, image_size, R, T, flags=flags)
    stereoMapL = cv2.fisheye.initUndistortRectifyMap(camera_matrix_left, dist_coeffs_left, R1, P1, image_size, cv2.CV_16SC2)
    stereoMapR = cv2.fisheye.initUndistortRectifyMap(camera_matrix_right, dist_coeffs_right, R2, P2, image_size, cv2.CV_16SC2)
    return stereoMapL, stereoMapR, Q

# Function to save the stereo rectification maps
def save_stereo_maps(stereoMapL, stereoMapR, Q, directory=STEREO_MAPS_DIR):
    """Save the stereo rectification maps to the specified directory."""
    os.makedirs(directory, exist_ok=True)
    np.save(os.path.join(directory, 'stereoMapL_x.npy'), stereoMapL[0])
    np.save(os.path.join(directory, 'stereoMapL_y.npy'), stereoMapL[1])
    np.save(os.path.join(directory, 'stereoMapR_x.npy'), stereoMapR[0])
    np.save(os.path.join(directory, 'stereoMapR_y.npy'), stereoMapR[1])
    np.save(os.path.join(directory, 'Q.npy'), Q)

# Function to process images
def process_images(left_images_dir, right_images_dir, output_dir):
    """Undistort and rectify the images and save them to the output directory."""
    left_images = sorted(glob.glob(os.path.join(left_images_dir, '*.jpg')))
    right_images = sorted(glob.glob(os.path.join(right_images_dir, '*.jpg')))
    os.makedirs(output_dir, exist_ok=True)

    # All images must have the same size
    first_left_image = cv2.imread(left_images[0])
    image_size = first_left_image.shape[1], first_left_image.shape[0]
    stereoMapL, stereoMapR, Q = initialize_stereo_rectification(image_size, camera_matrix_left, dist_coeffs_left, camera_matrix_right, dist_coeffs_right, R, T)

    # Save the maps for future use
    save_stereo_maps(stereoMapL, stereoMapR, Q)

    for left_img_path, right_img_path in zip(left_images, right_images):
        left_img = cv2.imread(left_img_path)
        right_img = cv2.imread(right_img_path)

        left_img_rectified = cv2.remap(left_img, stereoMapL[0], stereoMapL[1], cv2.INTER_LINEAR)
        right_img_rectified = cv2.remap(right_img, stereoMapR[0], stereoMapR[1], cv2.INTER_LINEAR)

        # Combine the images side-by-side
        combined = np.concatenate((left_img_rectified, right_img_rectified), axis=1)
        # Save the rectified images
        cv2.imwrite(os.path.join(output_dir, os.path.basename(left_img_path)), combined)

        print(f"Processed and saved {left_img_path} and {right_img_path}")

if __name__ == "__main__":
    process_images(LEFT_EYE_IMAGES_DIR, RIGHT_EYE_IMAGES_DIR, OUTPUT_DIR)
