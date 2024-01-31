## Average Fetch time
Performing a synchronous fetch of 1k images for each of the following 30 (FRAME_SIZE, JPEG_QUALITY) combinations (using [update_camera_config.py](https://github.com/Any-Winter-4079/GPT_Uno_Robot/blob/main/computer_code/test_scripts/camera/1_update_cam_config.py) as test script), latency varies from 0.027 (s) to 0.618 (s) -that is, from ~1.7 to 37 fps.

### M5Stack Wide Camera

| FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
|-----------------|----------------|----------------|-----------------|-----------------|-----------------|
| QVGA (320x240)  | Err            | 0.055          | 0.035           | 0.032           | 0.030           |
| VGA (640x480)   | 0.141          | 0.112          | 0.077           | 0.074           | 0.067           |
| SVGA (800x600)  | 0.177          | 0.126          | 0.113           | 0.075           | 0.067           |
| XGA (1024x768)  | 0.365          | 0.282          | 0.197           | 0.153           | 0.152           |
| SXGA (1280x1024)| 0.491          | 0.335          | 0.248           | 0.183           | 0.166           |
| UXGA (1600x1200)| 0.618          | 0.409          | 0.300           | 0.222           | 0.191           |

<div align="center"><img width="700" alt="Screenshot 2024-01-31 at 21 09 34" src="https://github.com/Any-Winter-4079/GPT_Uno_Robot/assets/50542132/77a86c6f-5b5e-4b12-bd2f-3ed7c434cd9c"></div>

### Ai-Thinker Camera

| FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
|-----------------|----------------|----------------|-----------------|-----------------|-----------------|
| QVGA (320x240)  | Err            | 0.039          | 0.029           | 0.030           | 0.027           |
| VGA (640x480)   | 0.139          | 0.118          | 0.074           | 0.075           | 0.068           |
| SVGA (800x600)  | 0.143          | 0.111          | 0.107           | 0.067           | 0.067           |
| XGA (1024x768)  | 0.286          | 0.269          | 0.182           | 0.148           | 0.150           |
| SXGA (1280x1024)| 0.374          | 0.258          | 0.212           | 0.173           | 0.155           |
| UXGA (1600x1200)| 0.503          | 0.307          | 0.218           | 0.221           | 0.194           |

<div align="center"><img width="700" alt="Screenshot 2024-01-31 at 21 10 05" src="https://github.com/Any-Winter-4079/GPT_Uno_Robot/assets/50542132/f1406ccf-bfca-4ed6-a7de-8df5745dcf23"></div>

