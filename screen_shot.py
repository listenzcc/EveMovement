"""
File: screen_shot.py
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
import cv2
import numpy as np
from PIL import ImageGrab, Image
from IPython.display import display
from qreader import QReader

# %% ---- 2025-02-13 ------------------------
# Function and class
x = 0+0*128
y = 1440-1080+0*94
w = 1920
h = 1080
padding = 0  # 10
snapshot = ImageGrab.grab(all_screens=True)
roi = snapshot.crop((x-padding, y-padding, x+w+padding, y+h+padding))
print(snapshot.size)
# display(snapshot)

print(roi.size)
# display(roi)


mat = np.zeros((100, 100), dtype=np.uint8)
d = 50
for j in range(100//d):
    for k in range(100//d):
        if j % 2 == k % 2:
            mat[d*j:d*j+d, d*k:d*k+d] = 255
img = Image.fromarray(mat)
img.save('img.png')
patch = Image.new('RGB', size=(100, 100), color='red')
patch.save('red.png')


def shot():
    x = 0+0*128
    y = 1440-1080+0*94
    w = 1920
    h = 1080
    snapshot = ImageGrab.grab(all_screens=True)
    roi = snapshot.crop((x-padding, y-padding, x+w+padding, y+h+padding))
    return roi


qreader = QReader()

while True:
    winname = 'Window'
    roi = shot()
    mat = cv2.cvtColor(np.array(roi), cv2.COLOR_RGB2BGR)
    r_channel = mat[:, :, 2]
    g_channel = mat[:, :, 1]
    b_channel = mat[:, :, 0]
    # print(mat.shape)

    found = qreader.detect_and_decode(
        image=mat[::2, ::2, :].copy(), return_detections=True)
    for f in found[1]:
        print(f['cxcy'])
        x, y = f['cxcy']
        x *= 2
        y *= 2
        mat[int(y)-10:int(y)+10, int(x)-10:int(x)+10] = (0, 0, 255)

    cv2.imshow(winname, mat)

    cv2.waitKey(1)


# %% ---- 2025-02-13 ------------------------
# Play ground


# %% ---- 2025-02-13 ------------------------
# Pending


# %% ---- 2025-02-13 ------------------------
# Pending
