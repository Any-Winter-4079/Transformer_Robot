To enable eye movement (recalling that the OV2640 cameras serve as the pupils, with their cables passing through the eye to connect to an ESP32-CAM mounted on the top of the robot's second level), the variant with a 75mm cable length and a 160º field of view is chosen over the option with a 10mm cable and a 66º field of view. This decision allows the 75mm cable to provide sufficient maneuverability for eye movements (up, down, left, and right) without the need to attach the larger ESP32-CAM directly to the eyes.

These models, however, come with a fisheye lens that reasonably distorts the images. The fisheye distortion, with its noticeable curvature, can be seen in a frame captured by one of the cameras, as illustrated in Figure 1.
<div align="center">
  <img width="350" alt="Screenshot 2024-02-21 at 15 29 37" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/460321fa-745b-4103-96fb-30084fec92f2">
  <p>Figure 1. Robot camera capture showing the noticeable curvature distortion of the fisheye lens.
</p>
</div>

Therefore, it's recommended to calibrate both cameras to eliminate this distortion as much as possible, aiding future processes like object detection, distance calculation, etc. For this purpose, the most common pattern of 10x7 squares (9x6 inner corners), provided by OpenCV, is printed. Using [1_store_images_to_calibrate](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/calibration/1_store_images_to_calibrate.py), frames from both cameras can be captured simultaneously (with a small margin of error) from our computer, which can then be used for the intrinsic and extrinsic calibrations of the cameras ([2_perform_calibration](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/calibration/2_perform_calibration.py)).

Note that any pair of frames where the pattern's corners (or the lines connecting them) are not recognized should be discarded (with a new calibration run afterwards). An example of incorrect detection is shown in Figure 2. It's also important to experiment with the distance of the pattern from the camera (bringing it closer if necessary), its tilt (avoiding excessive tilting if the quality isn't high), and the image quality (ensuring there are no desynchronizations between the cameras as quality increases and the ESP32-CAMs' workload goes up), to ensure the frames don't negatively contribute to the calibration.
<div align="center">
  <img width="650" alt="Screenshot 2024-02-21 at 15 34 31" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/d63a996f-5f04-4746-9340-81d9cbc0bd04">
  <p>Figure 2. Pair of images (left eye, right eye) with incorrect corner detection in the right frame, which should therefore be discarded.
</p>
</div>
