
After the calibration process, and once we've saved all the resulting parameters - matrices, distortion coefficients, rotation vectors, and translation vectors for both the right and left cameras (as part of the intrinsic calibration) and the rotation matrix, translation vector, essential matrix, and fundamental matrix (as part of the extrinsic calibration), it's wise to correct the distortion and rectify some images (whether the same ones from the calibration process or, even better, new images) with a small script ([undistort_and_rectify](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/undistortion_and_rectification/undistort_and_rectify.py)) to ensure that the calibration process parameters are accurate. Furthermore, this program can be used to save the stereo maps, which are beneficial for enhancing efficiency should this distortion correction and rectification need to be applied in the future (for example, to new frames captured by the robot).

In Figure 1, you can see a pair of left and right eye frames and their outcome after the distortion correction and rectification process.

<div align="center">
  <img width="776" alt="Screenshot 2024-02-21 at 15 55 17" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/c2c59b86-0020-461c-9472-32c31873848d">
<img width="778" alt="Screenshot 2024-02-21 at 15 55 29" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/ef7a9cd4-511f-47bd-8625-3c11276faea7">
  <p>Figure 1. A pair of images (left eye, right eye) at the top, and the same pair of frames after the distortion correction and rectification processes at the bottom.</p>
</div>
