import os
import re
import cv2
import glob
import numpy as np

#################
# Description   #
#################
# This is a program to calibrate the two ESP32-CAMs.
# We are using 2 OV2640, which have fisheye lenses, because of their 7.5cm cables,
# which allows us to pass the cable through the eye and plug it into the ESP32-CAM.
# Thus, the OpenCV fisheye calibration is used to calibrate the cameras.
# If you are using say a pinhole camera, you will need to remove .fisheye from the functions.

# The calibration is done in two steps:
# 1. Intrinsic calibration (calibrate each camera, separately). Obtains:
#    - Camera matrix
#    - Distortion coefficients
#    - Rotation vectors
#    - Translation vectors
# 2. Extrinsic calibration (calibrate both together for stereo). Obtains:
#    - Rotation matrix
#    - Translation vector
#    - Essential matrix
#    - Fundamental matrix

#################
# Notes         #
#################
# I ended up running this calibration script after every few image captures
# as a check for bad images (i.e. not taken 'simultaneously'). This helped keep the stereo calibration error low.
# If quality is not great, bringing the chessboard closer and not over-rotating it may help.
# If after calibration the corners are not detected well or the lines
# connecting them are not correct, you should remove the faulty image pairs and re-calibrate.
# If not enough images are left, you should run the previous script to capture more pairs.
# In the end, a lower (14) number of images seemed to work best for me, but in the past (a prior eye mechanism)
# I had had similar success with 40 images. A larger number, such as 130, did not work well for me, but it's
# hard to pinpoint the exact reason. A higher quality (such as the one used this time) may have improved
# corner detection but it may have worsened synchronization as well as the cameras struggle more to
# serve them.

#################
# Instructions  #
#################
# Before running this script, measure the chessboard square size in the real world and update SQUARE_SIZE.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Improvement   #
#################
# Using cornerSubPix can improve the quality of the corner detection.

#################
# Position      #
#################
# Make sure the cameras don't change their relative position
# to one another too much when the eyes move. Also, make sure the cameras are well
# aligned. My cameras were not perfectly aligned, but calibration still worked.
# Still, the better the alignment, probably the better the calibration.

#################
# Errors        #
#################
# Left Camera Calibration RMS Error: 0.2901713810526384
# Right Camera Calibration RMS Error: 0.28126123199806585
# Stereo Calibration RMS Error: 0.3137333419359242

# Apart from checking the error, make sure the undistorted images look good.
# See rectification/1_stereo_rectify.py for that.
# Usually, the intrinsic calibration error is easier to keep low than the stereo calibration error.

#################
# Configuration #
#################
SQUARE_SIZE = 2.45  # Update this with the measured square size in cm (here, 2.45cm)
CHESSBOARD_SIZE = (9, 6) # Even though the chessboard used has 10x7 squares, it has  9x6 inner corners. Yours may vary.
CORNER_SUBPIX_WINDOW_SIZE = (9, 9)  # Window size for cornerSubPix. Experiment with it.

# Prepare object points like (0,0,0), (1,0,0), (2,0,0) ..., (8,5,0)
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2) * SQUARE_SIZE

# Create arrays to store object points and image points from all images
objpoints = []  # 3D points in real-world space
imgpoints_left = []  # 2D points in image plane for left camera
imgpoints_right = []  # 2D points in image plane for right camera

# Load images from the two cameras
images_left = glob.glob('images/left_eye/*.jpg')
images_right = glob.glob('images/right_eye/*.jpg')

# Function to extract timestamp from filename
def extract_timestamp(filename):
    """
    Extracts the timestamp from the filename.
    Example filename: 'stereo_image_20240108_185627.jpg'
    """
    match = re.search(r'(\d{8}_\d{6})', filename)
    return match.group(0) if match else None

# Sort the images by their timestamps
images_left.sort(key=extract_timestamp)
images_right.sort(key=extract_timestamp)

# Ensure the same number of images for each camera
assert len(images_left) == len(images_right), "Different number of images for each camera"

# Ensure the directory to store the corner-marked side-by-side images exists
side_by_side_images_path = "images/corners_side_by_side"
os.makedirs(side_by_side_images_path, exist_ok=True)

# Clear previous images in the corner-marked side-by-side images directory
for path in [side_by_side_images_path]:
    files = glob.glob(f"{path}/*")
    for f in files:
        os.remove(f)

# Function to display two images side by side
def show_side_by_side(img1, img2, window_name='Side-by-side', display_time=500):
    """Show two images side by side for a specified time."""
    combined_image = np.concatenate((img1, img2), axis=1)
    cv2.imshow(window_name, combined_image)
    cv2.waitKey(display_time)
    cv2.destroyAllWindows()

# Function to save side-by-side images
def save_side_by_side(img1, img2, filename, output_dir=side_by_side_images_path):
    """Save side-by-side images."""
    combined_image = np.concatenate((img1, img2), axis=1)
    cv2.imwrite(os.path.join(output_dir, filename), combined_image)

# Define criteria for cornerSubPix
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Go through image pairs and find chessboard corners
for img_left, img_right in zip(images_left, images_right):
    # Check if timestamps match
    timestamp_left = extract_timestamp(img_left)
    timestamp_right = extract_timestamp(img_right)
    assert timestamp_left == timestamp_right, f"Timestamp mismatch: {img_left} and {img_right}"

    # Load images and convert to grayscale
    imgL = cv2.imread(img_left)
    imgR = cv2.imread(img_right)
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    # Find chessboard corners
    retL, cornersL = cv2.findChessboardCorners(grayL, CHESSBOARD_SIZE, None)
    retR, cornersR = cv2.findChessboardCorners(grayR, CHESSBOARD_SIZE, None)

    # If found in both images, add object points and image points
    if retL and retR:

        cornersL = cv2.cornerSubPix(grayL, cornersL, CORNER_SUBPIX_WINDOW_SIZE, (-1, -1), criteria)
        cornersR = cv2.cornerSubPix(grayR, cornersR, CORNER_SUBPIX_WINDOW_SIZE, (-1, -1), criteria)

        objpoints.append(objp.copy())
        imgpoints_left.append(cornersL)
        imgpoints_right.append(cornersR)

        # Draw and save corners
        imgL_drawn = cv2.drawChessboardCorners(imgL, CHESSBOARD_SIZE, cornersL, retL)
        imgR_drawn = cv2.drawChessboardCorners(imgR, CHESSBOARD_SIZE, cornersR, retR)

        # Display the images side-by-side
        show_side_by_side(imgL_drawn, imgR_drawn, "Chessboard Corners", 500)

        # Save side-by-side images with drawn corners
        side_by_side_filename = f"{timestamp_left}_side_by_side.jpg"
        save_side_by_side(imgL_drawn, imgR_drawn, side_by_side_filename)
    else:
        print(f"Chessboard corners not found for {img_left} and {img_right}")

# Now make sure the object points are a list of arrays with shape (N, 1, 3)
objpoints = [objp.reshape(-1, 1, 3) for _ in range(len(imgpoints_left))]

# Ensure that the image points are also lists of two-dimensional points
# and convert them to floating point
imgpoints_left = [ip.astype(np.float32) for ip in imgpoints_left]
imgpoints_right = [ip.astype(np.float32) for ip in imgpoints_right]

# Debug print to check the shapes and types again
print("Updated Object Points Shape and Type:", np.array(objpoints).shape, np.array(objpoints).dtype)
print("Image Points Left Shape and Type:", np.array(imgpoints_left).shape, np.array(imgpoints_left).dtype)
print("Image Points Right Shape and Type:", np.array(imgpoints_right).shape, np.array(imgpoints_right).dtype)


# Define the fisheye camera matrices and distortion coefficients arrays
K_left = np.zeros((3, 3))
D_left = np.zeros((4, 1))
K_right = np.zeros((3, 3))
D_right = np.zeros((4, 1))

# Define flags and criteria for fisheye calibration
flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC | cv2.fisheye.CALIB_CHECK_COND | cv2.fisheye.CALIB_FIX_SKEW
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

# Calibrate the left camera
try:
    rms_left, K_left, D_left, rvecs_left, tvecs_left = cv2.fisheye.calibrate(
        objpoints, imgpoints_left, grayL.shape[::-1], K_left, D_left, flags=flags, criteria=criteria
    )
    print(f"Left Camera Calibration RMS Error: {rms_left}")
except Exception as e:
    print("Left camera calibration failed:", e)

# Calibrate the right camera
try:
    rms_right, K_right, D_right, rvecs_right, tvecs_right = cv2.fisheye.calibrate(
        objpoints, imgpoints_right, grayR.shape[::-1], K_right, D_right, flags=flags, criteria=criteria
    )
    print(f"Right Camera Calibration RMS Error: {rms_right}")
except Exception as e:
    print("Right camera calibration failed:", e)

# Stereo calibration
try:
    rms_stereo, _, _, _, _, R, T, E, F = cv2.fisheye.stereoCalibrate(
        objpoints, imgpoints_left, imgpoints_right, K_left, D_left, K_right, D_right, grayL.shape[::-1], flags=cv2.fisheye.CALIB_FIX_INTRINSIC, criteria=criteria
    )
    print(f"Stereo Calibration RMS Error: {rms_stereo}")
except Exception as e:
    print("Stereo calibration failed:", e)

# Ensure output directory exists
os.makedirs('parameters', exist_ok=True)

# Print camera matrices
print("Camera Matrix Left Eye:\n", K_left)
print("Camera Matrix Right Eye:\n", K_right)

# Save calibration results
np.save('parameters/camera_matrix_right_eye.npy', K_right)
np.save('parameters/distortion_coeffs_right_eye.npy', D_right)
np.save('parameters/rotation_vec_right_eye.npy', rvecs_right)
np.save('parameters/translation_vec_right_eye.npy', tvecs_right)

np.save('parameters/camera_matrix_left_eye.npy', K_left)
np.save('parameters/distortion_coeffs_left_eye.npy', D_left)
np.save('parameters/rotation_vec_left_eye.npy', rvecs_left)
np.save('parameters/translation_vec_left_eye.npy', tvecs_left)

np.save('parameters/rotation_matrix.npy', R)
np.save('parameters/translation_vector.npy', T)
np.save('parameters/essential_matrix.npy', E)
np.save('parameters/fundamental_matrix.npy', F)

print("Calibration completed and results saved.")
