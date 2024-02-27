import os
import time
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt

#################
# Description   #
#################
# This is a script to perform face recognition using the DeepFace framework.
# This script is developed to work with known faces only.

#################
# Instructions  #
#################
# For testing, I used the following dataset:
# https://www.kaggle.com/hereisburak/pins-face-recognition
# Another dataset that looks interesting:
# https://www.kaggle.com/datasets/jessicali9530/lfw-dataset/data
# Of this dataset, I used 1439 images, moving their folders
# to a 'database' folder. So the directory structure is:
# database
# ├── Aaron_Eckhart
# │   ├── Aaron_Eckhart_0001.jpg
# ├── Aaron_Guiel
# │   ├── Aaron_Guiel_0001.jpg
# ...
# 1_benchmark_face_recognition_with_known_faces.py

# The 1439 images are divided into 786 folders, one per person. Note you can also
# place some images of yourself! The number of images in each folder varies
# in the dataset and it's something worth experimenting with.

# The test images are in the 'test_images' folder and they are chosen from the same dataset.
# Note the images in the 'test_images' folder must be removed from the 'database' folder.
# The directory structure is:
# database
# test_images
# ├── Aaron_Eckhart_0002.jpg
# ...
# 1_benchmark_face_recognition_with_known_faces.py

# Note not all people from the 'database' folder need to be in the 'test_images' folder.
# In my tests, a total of 30 images (people) were chosen for the 'test_images' folder.

# While test_backends() is designed to test the backends for a single model, you can
# change the model to see which combination works better. After n model calls,
# you should know which backend and model combination works better for your dataset.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
# You can add/remove backends and models depending on which ones you want to test
# Check the full list of backends and models at https://github.com/serengil/deepface
# Backends for face detection
# Models for face recognition
BACKENDS = [
  'opencv', 
  'ssd', 
  'mtcnn', 
  'retinaface', 
  'mediapipe',
  'yolov8',
  'yunet',
  'fastmtcnn',
]
MODELS = [
  "VGG-Face",
  "Facenet",
  "Facenet512",
  "OpenFace",
  "DeepID",
  "ArcFace"
]
DISTANCE_METRICS = ["cosine", "euclidean", "euclidean_l2"]
TEST_IMAGES_PATH = "test_images"
DATABASE_PATH = "database"
# THRESHOLD = 1.1 # (distances < this threshold will be returned from the find function.
# In other words, set how close the match should be. Lower values risk false negatives,
# high values risk getting false positives.)
# Note different metrics (and models) require different thresholds
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

# Set the model, backend, and distance metric
MODEL = MODELS[5]
BACKEND = BACKENDS[7] # This is for plot_recognition_times()
DISTANCE_METRIC = DISTANCE_METRICS[0]

# Function to validate the recognition
def validate_recognition(prediction, test_image_file):
    """Validate the recognition by comparing the predicted name with the actual name."""
    predicted_name = prediction.split('/')[-1]
    predicted_name = "_".join(predicted_name.split('_')[:-1])
    predicted_name = predicted_name.lower()
    print(f"Predicted name: {predicted_name}")

    actual_name = "_".join(test_image_file.split('_')[:-1])
    actual_name = actual_name.lower()
    print(f"Actual name: {actual_name}")
    return 1 if predicted_name == actual_name else 0

# Function to recognize a face in an image using the DeepFace library
def recognize_face(test_image_path, backend=BACKEND):
      """Recognize a face in an image using the DeepFace library."""
      try:
        dfs = DeepFace.find(
           img_path=test_image_path,
           db_path=DATABASE_PATH,
           model_name=MODEL,
           detector_backend=backend,
           distance_metric=DISTANCE_METRIC,
           enforce_detection=False,
           # threshold=THRESHOLD
        )
        # dfs is a list of dataframes, one dataframe per face recognized
        # test_images in this basic version are not meant for >1 face
        face = dfs[0]
        # Once we have the face, we return its top prediction
        return face.iloc[0] if len(face) > 0 else None
      except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {MODEL} and backend {backend}: {e}\n")

# Function to plot the recognition times
def plot_recognition_times():
    """Plot the recognition times for each test image using a specified backend."""

    # Build model for faster performance, but at the same time, building the model
    # is what (I think) takes the most time, so if we looped here for >1 backend,
    # the first backend would seemingly have a spike in the first image,
    # while the other backends would not (because they would take advantage of the
    # already built model).
    DeepFace.build_model(MODEL)
    
    times = []
    test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
    
    for test_image_file in test_image_files:
        test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
        start_time = time.time()
        _ = recognize_face(test_image_path)
        end_time = time.time()
        times.append(end_time - start_time)
    
    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(test_image_files)), times, edgecolor='black', color='#4BA081',)
    plt.xlabel('Test Image')
    plt.ylabel('Recognition time (s)')
    plt.title(f'Recognition times for {BACKEND} and {MODEL}')
    plt.xticks(range(len(test_image_files)), labels=[f.split('.')[0] for f in test_image_files], rotation=90)
    plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

# Function to plot the backend comparison
def plot_backend_comparison(results, test_image_files):
    """Plot the backend comparison."""
    backends = list(results.keys())
    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_predictions = [results[backend]["correct_predictions"] for backend in backends]

    fig, ax1 = plt.subplots()

    color = '#4BA081'
    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Correct recognitions', color='black')
    bars = ax1.bar(backends, correct_predictions, color=color, edgecolor='black', label='Correct recognitions')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xticks(range(len(backends)))
    ax1.set_xticklabels(backends, rotation=45, ha="right")
    ax1.set_ylim(0, len(test_image_files))

    for bar in bars:
        height = bar.get_height()
        ax1.annotate('{}'.format(height),
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')

    ax2 = ax1.twinx()
    color = '#387761'
    ax2.set_ylabel('Average time (s)', color='black')
    ax2.plot(backends, average_times, color=color, marker='o', linestyle='-', linewidth=2, markersize=5)
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

    fig.tight_layout()
    plt.title(f'Correct predictions (bars) and average time (lines) for {MODEL}')
    plt.show()

 # Function to test the backends for face recognition
def test_backends():
    """Test the backends for face recognition."""
    results = {}
    for backend in BACKENDS:

      # Build model for faster performance
      DeepFace.build_model(MODEL)

      predictions = {
          "correct_predictions": 0,
          "times": []
          }
      test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
      for test_image_file in test_image_files:
          test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
          start_time = time.time()
          result = recognize_face(test_image_path, backend)
          end_time = time.time()
          predictions["correct_predictions"] += validate_recognition(result['identity'], test_image_file) if result is not None else 0
          predictions["times"].append(end_time - start_time)
      results[backend] = predictions

    # Plot the results:
    plot_backend_comparison(results, test_image_files)

    # Print the results
    backends = list(results.keys())
    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_predictions = [results[backend]["correct_predictions"] for backend in backends]
    for backend in BACKENDS:
      print(f"Backend: {backend}")
      print(f"\tAverage time: {average_times[backends.index(backend)]:.4f} seconds")
      print(f"\tCorrect predictions: {correct_predictions[backends.index(backend)]} out of {len(test_image_files)}\n")

if __name__ == "__main__":
    test_backends()
    #plot_recognition_times() # Run without running test_backends() to account for the model building time
