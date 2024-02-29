import os
import time
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt

#################
# Description   #
#################
# This is a script to perform face recognition using the DeepFace framework.
# This script is developed to work with both known and unknown faces
# and even with images that do not contain faces.

#################
# Instructions  #
#################
# Startint with the database from the previous script, I added:
# Tom_Cruise, Salma_Hayek, and Valentino_Rossi from the full dataset, making it
# 4 known people (with Arnold_Schwarzenegger, already there for starting with 'A').
# 3 more images are added to the database for each of these 4 people,
# given side_close, side_far and front_far images seem rare on the
# LFW dataset.

# All images are resized to the same size, in this case, 250x250 pixels, which
# is the default size for this dataset. This includes new images added to
# the database and test images.

# Test images are in the '2_test_images' folder and they are are chosen from the internet.
# Specifically: (known) Salma_Hayek, (known) Tom_Cruise, (known) Valentino_Rossi, (known) Arnold_Schwarzenegger
# (unknown) Curry, (unknown) Shaq, (unknown) Emma_Roberts, (unknown) Vanessa_Hudgens, (unknown) unknown_0001-0016
# Test images (showing faces) are taken in four 'flavors': front_close, front_far, side_close, side_far.
# The directory structure is:
# test_images
# ├── Salma_Hayek_front_close_known_0001.jpg
# ├── Salma_Hayek_front_far_known_0002.jpg
# ├── Salma_Hayek_side_close_known_0002.jpg
# ├── Salma_Hayek_side_far_known_0002.jpg
# ├── Curry_front_close_unknown_0001.jpg
# ├── Curry_front_far_unknown_0002.jpg
# ├── Curry_side_close_unknown_0003.jpg
# ├── Curry_side_far_unknown_0004.jpg
# ├── unknown_0001.jpg
# ...
# 2_benchmark_face_recognition_with_unknown_and_no_faces.py

# So to recap, 4 known people (with 4 images each), 4 unknown people (with 4 images each) and 16 images without faces.

# Names can have a _surname or not, and both should work well.

#################
# Notes         #
#################
# While test_backends() is designed to test the backends for a single model, you can
# change the model to see which combination works better. After n model calls,
# you should know which backend and model combination works better for your dataset.
# After you close the plot, a second plot will be shown with the 'flavor' stats
# (front_close, front_far, side_close, side_far).

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
TEST_IMAGES_PATH = "2_test_images" # make sure to create this folder and place some images there
DATABASE_PATH = "2_database" # make sure to create this folder and place some images there
# THRESHOLD = 0.5 # (distances < this threshold will be returned from the find function.
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
MODEL = MODELS[0]
BACKEND = BACKENDS[7] # This is for plot_recognition_times()
DISTANCE_METRIC = DISTANCE_METRICS[0]

# Function to validate the recognition
def validate_recognition(prediction, test_image_file):
    """Validate the recognition by comparing the predicted name with the actual name."""
    correct_identification = 0
    correct_non_identification = 0
    identification_types = {
        'front_close': 0,
        'front_far': 0,
        'side_close': 0,
        'side_far': 0,
    }

    # This assumes the naming convention from above!
    actual_name_parts = test_image_file.split('/')[-1].split('_')
    actual_is_unknown = "unknown" in test_image_file
    identification_type = "_".join(actual_name_parts[-4:-2]) if len(actual_name_parts) > 4 else None

    # actual_name refers to the name of the person in the test_image_file
    # predicted_name refers to the top match's filename in the database
    if actual_is_unknown:
        actual_name = "unknown"
    else:
        actual_name = '_'.join(actual_name_parts[:-4]).lower()

    print(f"Actual name: {actual_name}")

    if not prediction:
        print("Predicted name: unknown")
        if actual_is_unknown:
            correct_non_identification = 1
    elif prediction:
        top_prediction = prediction[0]
        identity = top_prediction["identity"]
        predicted_name = "_".join(identity.split('/')[-1].split('_')[:-1]).lower()
        print(f"Predicted name: {predicted_name}")

        if predicted_name == actual_name:
            correct_identification = 1
            identification_types[identification_type] += 1

    return correct_identification, correct_non_identification, identification_types


# Function to get the top predictions
def get_top_predictions(dfs_list):
    """Extract the top prediction for each person from the list of dataframes."""
    # The list can have more than one dataframe if there are multiple faces.
    # One dataframe per face.
    # Each dataframe has one or more rows, from most likely to least likely
    # while meeting the threshold.
    top_predictions = []
    if dfs_list is not None:
      for df in dfs_list:
          if len(df) > 0:
              top_prediction = df.iloc[0]
              top_predictions.append(top_prediction)
    return top_predictions

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
        top_predictions = get_top_predictions(dfs)
        return top_predictions # return top prediction for each face in the image
      except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {MODEL} and backend {backend}: {e}\n")

# Function to plot the recognition times
def plot_recognition_times():
  """Plot the recognition times for each test image using a specified backend."""

  # Build model for faster performance, but at the same time, building the model
  # is what (I think) takes the most time, so if we looped here for >1 backend,
  # the first backend would seemingly have a spike in the first image,
  # while the other backends would not (because they would take advantage of the
  # already built model). But given the purpose is to see the spike,
  # we leave it this way.
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
  plt.xlabel('Test image')
  plt.ylabel('Recognition time (s)')
  plt.title(f'Recognition times for {BACKEND} and {MODEL}')
  plt.xticks(range(len(test_image_files)), labels=[f.split('.')[0] for f in test_image_files], rotation=90)
  plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
  plt.tight_layout()
  plt.show()

# Function to test the backends for face recognition
def test_backends():
    """Test the backends for face recognition."""
    results = {}
    for backend in BACKENDS:

      # Build model for faster performance
      DeepFace.build_model(MODEL)

      predictions = {
          "correct_identifications": 0,
          "correct_non_identifications": 0,
          "identification_types": {
              'front_close': 0,
              'front_far': 0,
              'side_close': 0,
              'side_far': 0,
          },
          "times": []
          }
      test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
      for test_image_file in test_image_files:
          test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
          start_time = time.time()
          result = recognize_face(test_image_path, backend=backend)
          end_time = time.time()
          correct_identification, correct_non_identification, identification_types = validate_recognition(result, test_image_file)
          predictions["correct_identifications"] += correct_identification
          predictions["correct_non_identifications"] += correct_non_identification
          for id_type in identification_types:
            predictions["identification_types"][id_type] += identification_types[id_type]
          predictions["times"].append(end_time - start_time)
      results[backend] = predictions

    # Plot the results
    backends = list(results.keys())

    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_identifications = [results[backend]["correct_identifications"] for backend in backends]
    correct_non_identifications = [results[backend]["correct_non_identifications"] for backend in backends]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    index = np.arange(len(backends))
    rects1 = ax1.bar(index - bar_width/2, correct_identifications, bar_width, label='Correct identifications', color='#4BA081', edgecolor='black')

    rects2 = ax1.bar(index + bar_width/2, correct_non_identifications, bar_width, label='Correct non-identifications', color='#388872', edgecolor='black')

    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Number of correct predictions', color='black')
    ax1.set_title(f'Recognition performance for {MODEL} and {DISTANCE_METRIC}')
    ax1.set_xticks(index)
    ax1.set_xticklabels(backends, rotation=45, ha="right")
    ax1.legend()

    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax1.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax2 = ax1.twinx()  
    ax2.set_ylabel('Average time (s)', color='black')
    ax2.plot(backends, average_times, color='#387761', marker='o', linestyle='-', linewidth=2, markersize=5, label='Average time')
    ax2.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.legend(loc='upper center')

    fig.tight_layout()
    plt.show()

    # Plot Identification Types
    n_backends = len(results)
    n_types = 4
    bar_width = 0.15
    spacing = 0.05

    backends = list(results.keys())
    id_types = ['front_close', 'front_far', 'side_close', 'side_far']
    data = np.array([[results[backend]["identification_types"][id_type] for id_type in id_types] for backend in backends])

    index = np.arange(n_backends) * (n_types * bar_width + spacing)

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#4BA081', '#388872', '#83A598', '#B8B8B8']

    for i, id_type in enumerate(id_types):
      bars = ax.bar(index + i * bar_width, data[:, i], bar_width, label=id_type, color=colors[i], edgecolor='black')
      for bar in bars:
          height = bar.get_height()
          ax.annotate(f'{height}',
                      xy=(bar.get_x() + bar.get_width() / 2, height),
                      xytext=(0, 3),
                      textcoords="offset points",
                      ha='center', va='bottom')

    ax.set_xlabel('Backends')
    ax.set_ylabel('Counts')
    ax.set_title(f'Counts per image type for {MODEL} and {DISTANCE_METRIC}')
    ax.set_xticks(index + bar_width * (n_types - 1) / 2)
    ax.set_xticklabels(backends, rotation=45)
    ax.legend(title="Identification types")

    ax.set_xlim(-bar_width, max(index) + bar_width * n_types + spacing)

    plt.tight_layout()
    plt.show()

    # Print the results
    for backend in backends:
      print(f"Backend: {backend}")
      print(f"\tAverage time: {average_times[backends.index(backend)]:.4f} seconds")
      print(f"\tCorrect identifications: {correct_identifications[backends.index(backend)]}")
      print(f"\tCorrect non-identifications: {correct_non_identifications[backends.index(backend)]}")
      print(f"\tIdentification types: {results[backend]['identification_types']}\n")

if __name__ == "__main__":
    test_backends()
    #plot_recognition_times() # Run without running test_backends() to account for the model building time
