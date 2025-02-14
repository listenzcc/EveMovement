"""
File: process_target.py
Author: Chuncheng Zhang
Date: 2025-02-13
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-02-13 ------------------------
# Requirements and constants
from tqdm.auto import tqdm
import cv2
import numpy as np
from PIL import Image, ImageDraw


# %% ---- 2025-02-13 ------------------------
# Function and class


# %% ---- 2025-02-13 ------------------------
# Play ground
target_img = Image.open('target.png')
display(target_img)

mat = np.array(target_img)

display(Image.fromarray(mat))

# %% ---- 2025-02-13 ------------------------
# Pending
# Convert to HSV
hsv = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)

# Define the red color range
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 100, 100])
upper_red2 = np.array([180, 255, 255])

# Create masks for red color
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
mask = mask1 | mask2

# Morphological operations
mask = cv2.erode(mask, None, iterations=2)
mask = cv2.dilate(mask, None, iterations=2)

# Find contours
contours, _ = cv2.findContours(
    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw the contours on the original image
for contour in tqdm(contours):
    if cv2.contourArea(contour) > 100:  # Filter by area
        cv2.drawContours(mat, [contour], -1, (0, 255, 0), 3)
        x, y = np.mean(contour.squeeze(), axis=0)
        print(x, y)

# Show the result
display(Image.fromarray(mat))

# cv2.imshow('Red Ring Detection', mat)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# %% ---- 2025-02-13 ------------------------
# Pending

# %%
