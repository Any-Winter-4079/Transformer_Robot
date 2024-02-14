Given that different tasks—such as object detection, person recognition, depth estimation, etc.—may require different models and libraries (TensorFlow, YOLOv8, MediaPipe, OpenCV, etc.), and these can have varying computing times (to detect the object, recognize the person, etc.) and require different image qualities to function correctly, it's important to find a balance between the requirements of the used models and libraries and those of the robot's task (for example, a driving task, where the scene constantly changes, with lane changes, signals, etc., may require a higher frame rate than a person recognition task when talking to an interlocutor—to refer to them by their name—, which generally will not change as quickly). Therefore, it is necessary to find an image size and quality that can be processed by the libraries with the highest possible performance—which may require a larger size or quality of frame—, but always meeting the frame rate of the robot's task.

Note that, for this reason, it is decided to include /camera_config in the ESP32-CAMs, to be able to change size and quality on-the-fly depending on the task to be completed. Likewise, other parameters, such as clock speed or number of buffers, could be made configurable in the same way, but after several tests, it is considered sufficient to work consistently with 1 buffer and at 20MHz.

As a first step, and to get an idea of the maximum possible performance by the ESP32-CAMs, the following study is carried out, requesting (synchronously) a total of 1,000 frames for each of the following 30 combinations of size and quality, and calculating their average fetch time.

Observing the results (Table 1 for M5Stack Wide and Table 2 for Ai-Thinker), it can be seen how latency varies from 0.027 to 0.618 seconds—i.e., from ~1.7 to 37 fps.

| FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
|-----------------|----------------|----------------|-----------------|-----------------|-----------------|
| QVGA (320x240)  | Err            | 0.045          | 0.035           | 0.032           | 0.030           |
| VGA (640x480)   | 0.141          | 0.112          | 0.077           | 0.074           | 0.067           |
| SVGA (800x600)  | 0.177          | 0.126          | 0.113           | 0.075           | 0.067           |
| XGA (1024x768)  | 0.365          | 0.282          | 0.197           | 0.153           | 0.152           |
| SXGA (1280x1024)| 0.491          | 0.335          | 0.248           | 0.183           | 0.166           |
| UXGA (1600x1200)| 0.618          | 0.409          | 0.300           | 0.222           | 0.191           |

<div align="center">
  <p>Table 1. Average fetch time for 1000 iterations in 30 ESP32-CAM configurations of the M5Stack Wide model (in seconds).</p>
</div>

| FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
|-----------------|----------------|----------------|-----------------|-----------------|-----------------|
| QVGA (320x240)  | Err            | 0.039          | 0.029           | 0.030           | 0.027           |
| VGA (640x480)   | 0.139          | 0.118          | 0.074           | 0.075           | 0.068           |
| SVGA (800x600)  | 0.143          | 0.111          | 0.107           | 0.067           | 0.067           |
| XGA (1024x768)  | 0.286          | 0.269          | 0.182           | 0.148           | 0.150           |
| SXGA (1280x1024)| 0.374          | 0.258          | 0.212           | 0.173           | 0.155           |
| UXGA (1600x1200)| 0.503          | 0.307          | 0.218           | 0.221           | 0.194           |

<div align="center">
  <p>Table 2. Average fetch time for 1000 iterations in 30 ESP32-CAM configurations of the Ai-Thinker model (in seconds).</p>
</div>

It is important to highlight that the configuration sent to /camera_config of each ESP32-CAM is only valid until the next time a (re)boot is performed, at which point the default configuration recorded in the module is loaded (potentially, another size and/or quality of frame), so, in the event of an unexpected crash and despite the camera reinitializing and returning to operate normally, the size and quality may not be the desired ones, which is why, after a timeout where the camera is not able to deliver a frame, it is recommended, once the flow of frames is recovered, to send the configuration to /camera_config again.

The script to update the frame size and quality, and obtain the average fetch times, can be seen on [Github](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/test_scripts/camera/1_update_cam_config.py).

Graphically, and although the results must be taken with caution, since it is a single run per configuration (of 1000 iterations, but a single execution, so a momentary slowdown of the frame rate can significantly affect the average time), and different scenes can also lead to variations in these fps, they are presented in Figure 1 and Figure 2.

<div align="center"><img width="550" alt="Screenshot 2024-01-31 at 21 09 34" src="https://github.com/Any-Winter-4079/GPT_Uno_Robot/assets/50542132/77a86c6f-5b5e-4b12-bd2f-3ed7c434cd9c">
<p>Figure 1. Average fetch time for 1000 iterations in 30 ESP32-CAM configurations of the M5Stack Wide model (in seconds).</p></div>

<div align="center"><img width="550" alt="Screenshot 2024-01-31 at 21 10 05" src="https://github.com/Any-Winter-4079/GPT_Uno_Robot/assets/50542132/f1406ccf-bfca-4ed6-a7de-8df5745dcf23">
<p>Figure 2. Average fetch time for 1000 iterations in 30 ESP32-CAM configurations of the Ai-Thinker model (in seconds).</p>
</div>
