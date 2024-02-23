import argparse
import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose
from tqdm import tqdm

from depth_anything.depth_anything.dpt import DepthAnything
from depth_anything.depth_anything.util.transform import Resize, NormalizeImage, PrepareForNet

#################
# Description   #
#################
# This is a slightly modified version of the Depth Anything run.py to calculate the depth map of a single image.
# https://github.com/LiheYoung/Depth-Anything

#################
# Instructions  #
#################
# Clone the Depth Anything repository (inside the 'depth' folder) and rename it to depth_anything.
# Replace run.py and dpt.py (inside a second depth_anything folder) with the provided files.
# The structure should look like this:
# depth
# ├── depth_anything
# │   ├── depth_anything
# │   │   ├── dpt.py
# │   └── run.py
# ├── 2_calculate_depth_with_depth_anything.py

#################
# Configuration #
#################
ENCODER='vits' # can also be 'vitb' or 'vitl'

# Set device (CUDA, mps, cpu)
if torch.backends.mps.is_available():
    # print("Metal GPU available!")
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    # print("Using CUDA with GPU.")
else:
    DEVICE = torch.device("cpu")
    # print("Metal GPU not available. Using CPU.")
    
depth_anything = DepthAnything.from_pretrained('LiheYoung/depth_anything_{}14'.format(ENCODER)).to(DEVICE).eval()

total_params = sum(param.numel() for param in depth_anything.parameters())
print('Total parameters: {:.2f}M'.format(total_params / 1e6))

def get_depth(raw_image, grayscale=False):
    """Get depth map from an image using Depth Anything"""
    
    transform = Compose([
        Resize(
            width=518,
            height=518,
            resize_target=False,
            keep_aspect_ratio=True,
            ensure_multiple_of=14,
            resize_method='lower_bound',
            image_interpolation_method=cv2.INTER_CUBIC,
        ),
        NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        PrepareForNet(),
    ])
    
    image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB) / 255.0
    
    h, w = image.shape[:2]
    
    image = transform({'image': image})['image']
    image = torch.from_numpy(image).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        depth = depth_anything(image)
    
    depth = F.interpolate(depth[None], (h, w), mode='bilinear', align_corners=False)[0, 0]
    depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
    
    depth = depth.cpu().numpy().astype(np.uint8)
    
    if grayscale:
        depth = np.repeat(depth[..., np.newaxis], 3, axis=-1)
    else:
        depth = cv2.applyColorMap(depth, cv2.COLORMAP_INFERNO)
    
    return depth
    
