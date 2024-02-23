To facilitate navigation tasks, it is necessary to integrate the ability to detect obstacles, especially those close enough to the robot to pose a risk of collision.

In this case, and given that binocular vision is available, we implement and compare two approaches: Semi-Global Block Matching (SGBM), using the frames from both cameras to obtain a single final image with the depth map of the scene, and Depth Anything, a new model (2024) built on the DINOv2 encoder that allows for monocular depth estimation - that is, using a single camera.

The first implementation ([calculate_depth_map_on_face_detection_with_SGBM](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/depth/1_calculate_depth_map_on_face_detection_with_SGBM.py)) is pretty fast, with an average of ~0.07 seconds per depth map, sufficient to allow an acceptable frame rate for many navigation tasks. The depth maps, as can be seen in Figure 1, however, have quite a bit of noise (either due to the accumulation of small calibration/undistortion/rectification errors or algorithm limitations), and although playing with the parameters can homogenize the colors (for example, a relatively constant black for distant objects, reducing noise), the trade-off is at the expense of a lower level of detail (as can be seen in the lower images of Figure 1).
<div align="center">
  <img height="260" alt="Screenshot 2024-02-23 at 14 49 19" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/e4d4adcf-6741-4ce1-844c-7fc128922f0b">
  <img height="260" alt="Screenshot 2024-02-23 at 14 49 58" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/e4078b82-9b25-415f-8018-984ba6f97758">
  <img height="260" alt="Screenshot 2024-02-23 at 14 52 41" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/772da5c4-9278-4304-9934-6f03ece38620">
  <img height="260" alt="Screenshot 2024-02-23 at 14 53 52" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/e9c1a27c-c8e6-4654-a6f6-fd2e0ba246e2">
  <p>Figure 1. Depth maps of 4 images, resulting from applying SGBM to 4 pairs of frames (left eye, right eye) captured by the robot's cameras. From top to bottom and left to right, a person (me) with hands together, showing palms, hands joined under the chin, and thumbs up, noting that dark colors indicate depth and light colors, proximity.</p>
</div>

In fact, a set of trackbars is implemented - see Figure 2 - to be able to update these parameters in real-time, but the results are still mediocre, and, given that in a manually assembled robot the precision of the camera alignment is not the best (as opposed to a more millimetric 3D design), added to a medium-low frame quality (imposed by the ESP32-CAMs themselves), and observing some of the results from other projects ([example](https://www.youtube.com/watch?v=zDCLaCIGhD8), [example](https://www.youtube.com/watch?v=jhOTm3MZDaY), [example](https://www.youtube.com/watch?v=gffZ3S9pBUE)), it is considered unlikely to improve results without a significant change in the construction and components of the robot.

<div align="center">
  <img width="350" alt="Screenshot 2024-02-23 at 14 56 15" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/2beae73d-f598-4e56-b0a6-693631185265">
  <p>Figure 2. Depth map of 1 image, resulting from applying SGBM to 2 frames (left eye, right eye) captured by the robot's cameras. In the image, a person is seen with one hand behind their head and the other, near the camera, with a thumbs up.</p>
</div>

With the second implementation ([calculate_depth_with_depth_anything](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/depth/2_calculate_depth_with_depth_anything.py)), and after some modification to run on my M1 (Mac) GPU, it quickly becomes apparent that the quality (even with the smallest version of the model) is much higher, and, with a computation time of ~0.1 seconds per frame (compared to ~0.07 with SGBM), it quickly becomes evident that it is the correct choice. In Figure 3, the result of a pair of monocular depth maps, taken under the same conditions as those shown with SGBM, can be observed.

<div align="center">
  <img height="300" alt="Screenshot 2024-02-23 at 22 31 20" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/d7c44fdb-b142-47f8-a30d-ae4e30176ca4">
<img height="300" alt="Screenshot 2024-02-23 at 22 31 27" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/580956d8-7bf5-452e-9928-709c8a5bc7e4">
  <p>Figure 3. Depth map of 2 images, using Depth Anything and the robot's right eye camera. From left to right, a person (me) in a chair with thumbs up and showing the palm of the left hand, and with two thumbs up, respectively.</p>
</div>

It is worth noting that, just as SGBM allows for the calculation of the depth value given a pair of points (for example, in the SGBM script, the centroids of the face in the left and right frames are obtained, to calculate the depth, if desired) through triangulation, with this alternative (Depth Anything), an attempt could be made to obtain the metric value equally. However, it is considered that the current depth map - in the form of an image - may be sufficient if interpreted by an LLM, especially in environments where there is not a large number of changing obstacles (for example, indoor circuit driving).

In changing environments - such as outdoor driving, another possibility would be to add one or several depth sensors, which although sometimes may present problems for some materials (which absorb/scatter the signal differently and can cause it not to return with sufficient intensity), their installation in conjunction with other techniques (such as depth map), probably represents a more robust solution.
