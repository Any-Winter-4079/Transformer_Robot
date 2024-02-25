import os
import time
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt

#################
# Description   #
#################
# This is a script to perform face recognition using the DeepFace library.

#################
# Instructions  #
#################
# For testing, I used the following dataset:
# https://www.kaggle.com/hereisburak/pins-face-recognition
# Another dataset that looks interesting:
# https://www.kaggle.com/datasets/jessicali9530/lfw-dataset/data
# Of this dataset, I used 1469 images, moving their folders
# to a 'database' folder. So the directory structure is:
# database
# ├── Aaron_Eckhart
# │   ├── Aaron_Eckhart_0001.jpg
# ├── Aaron_Guiel
# │   ├── Aaron_Guiel_0001.jpg
# ...

# The 1469 images are divided into 786 folders, one per person. Note you can also
# place some images of yourself!

# The test images are in the 'test_images' folder and they are chosen from the same dataset.
# Note the images in the 'test_images' folder must be removed from the 'database' folder.
# The directory structure is:
# test_images
# ├── Aaron_Eckhart_0002.jpg
# ...

# Note not all people from the 'database' folder need to be in the 'test_images' folder.
# In my tests, a total of 30 images were chosen for the 'test_images' folder.

# While test_backends() is designed to test the backends for face recognition, you can also
# change the model to see which combination works better. After n models calls,
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
TEST_IMAGES_PATH = "test_images" # make sure to create this folder and place some images there
DATABASE_PATH = "database" # make sure to create this folder and place some images there
THRESHOLD = 1.1 # (distances < this threshold will be returned from the find function.
# In other words, set how close the match should be. Lower values risk getting no matches)

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
def recognize_face(backend, model, test_image_path, database_path, distance_metric, threshold):
      """Recognize a face in an image using the DeepFace library."""
      try:
        dfs = DeepFace.find(
           img_path=test_image_path,
           db_path=database_path,
           model_name=model,
           detector_backend=backend,
           distance_metric=distance_metric,
           enforce_detection=False,
           threshold=threshold)
        dataframe = dfs[0] # get the dataframe from the list of dataframes
        return dataframe.iloc[0] if len(dataframe) > 0 else None # return the first row if there are any
      except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {model} and backend {backend}: {e}\n")

# Function to plot the recognition times
def plot_recognition_times(backend):
  """Plot the recognition times for each test image using a specified backend."""
  model = MODELS[5]
  distance_metric = DISTANCE_METRICS[2]
  # Build model for faster performance
  DeepFace.build_model(model)
  
  times = []
  test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
  
  for test_image_file in test_image_files:
      test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
      start_time = time.time()
      _ = recognize_face(backend, model, test_image_path, DATABASE_PATH, distance_metric, THRESHOLD)
      end_time = time.time()
      times.append(end_time - start_time)
  
  # Plot the results
  plt.figure(figsize=(10, 6))
  plt.bar(range(len(test_image_files)), times, edgecolor='black', color='#4BA081',)
  plt.xlabel('Test Image')
  plt.ylabel('Recognition time (s)')
  plt.title(f'Recognition times for {backend} and {model}')
  plt.xticks(range(len(test_image_files)), labels=[f.split('.')[0] for f in test_image_files], rotation=90)
  plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
  plt.tight_layout()
  plt.show()       

# Function to test the backends for face recognition
def test_backends():
    """Test the backends for face recognition."""
    results = {}
    for backend in BACKENDS:
      model = MODELS[5]
      distance_metric = DISTANCE_METRICS[2]
      # Build model for faster performance
      DeepFace.build_model(model)

      predictions = {
          "correct_predictions": 0, # with this value, we will plot the number of correct predictions
          "times": [] # here the first recognition is slower, so we may want to plot the time for each recognition
          # apart from th average time across all predictions (correct or not).
          }
      test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
      for test_image_file in test_image_files:
          test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
          start_time = time.time()
          result = recognize_face(backend, model, test_image_path, DATABASE_PATH, distance_metric, THRESHOLD)
          end_time = time.time()
          predictions["correct_predictions"] += validate_recognition(result['identity'], test_image_file) if result is not None else 0
          predictions["times"].append(end_time - start_time)
      results[backend] = predictions

    # Plot the results
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
      ax1.annotate('{}'.format(round(height, 2)),
                  xy=(bar.get_x() + bar.get_width() / 2, height),
                  xytext=(0, 3),
                  textcoords="offset points",
                  ha='center', va='bottom', fontsize=9)

    ax2 = ax1.twinx() # instantiate a second axes that shares the same x-axis
    color = '#387761'
    ax2.set_ylabel('Average time (s)', color='black')
    ax2.plot(backends, average_times, color=color, marker='o', linestyle='-', linewidth=2, markersize=5)
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

    fig.tight_layout()
    plt.title(f'Correct predictions (bars) and average time (lines) for {model}')
    plt.show()

    # Print the results
    for backend in backends:
      print(f"Backend: {backend}")
      print(f"\tAverage time: {average_times[backends.index(backend)]:.4f} seconds")
      print(f"\tCorrect predictions: {correct_predictions[backends.index(backend)]} out of {len(test_image_files)}\n")

if __name__ == "__main__":
    # test_backends()
    plot_recognition_times(BACKENDS[7])
