"""
File: eye-movement-loop.py
Author: Chuncheng Zhang
Date: 2025-02-14
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


# %% ---- 2025-02-14 ------------------------
# Requirements and constants
import time
import cv2
import json
import numpy as np
from PIL import Image, ImageFile
import socket
import threading
import base64
import io
from qreader import QReader

winname = 'Window'
mat = None
gaze_data = None
scene_data = None
found = ((), [])
data_lock = threading.RLock()

# Handle truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# %% ---- 2025-02-14 ------------------------
# Function and class


def handle_client_connection(client_socket):
    print("Client connection established")
    global gaze_data, scene_data
    buffer = b''
    while True:
        message = client_socket.recv(4096)
        if not message:
            break
        buffer += message
        while len(buffer) >= 8:
            length = int(buffer[:8])
            if len(buffer) < 8 + length:
                break
            data = buffer[8:8 + length]
            buffer = buffer[8 + length:]
            with data_lock:
                if data.startswith(b'gaze'):
                    gaze_data = json.loads(data[4:])
                elif data.startswith(b'scene'):
                    # Convert data[5:] into PIL image directly
                    scene_data = io.BytesIO(base64.b64decode(
                        data[5:] + b'=' * (-len(data[5:]) % 4)))
    client_socket.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 19931))
server.listen(5)
print('Listening on port 19931')

threading.Thread(target=lambda: handle_client_connection(
    server.accept()[0]), daemon=True).start()

qreader = QReader()


def detect_qrcode():
    global found, mat
    while True:
        if mat is None:
            time.sleep(0.1)
            continue
        found = qreader.detect_and_decode(
            image=mat[::2, ::2, :].copy(), return_detections=True)


threading.Thread(target=detect_qrcode, daemon=True).start()

# %% ---- 2025-02-14 ------------------------
# Play ground
while True:
    time.sleep(0.1)

    with data_lock:
        try:
            fx, fy = gaze_data[1]['gaze2d']
        except:
            continue

        try:
            img = Image.open(scene_data)
            mat = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            w, h = img.size
        except:
            continue

    for f in found[1]:
        print(f['cxcy'])
        x, y = f['cxcy']
        x *= 2
        y *= 2
        mat[int(y)-10:int(y)+10, int(x)-10:int(x)+10] = (0, 255, 0)

    fx = int(fx * w)
    fy = int(fy * h)

    mat[fy-10:fy+10, fx-10:fx+10, 2] = 255
    cv2.imshow(winname, mat)
    cv2.waitKey(1)

cv2.destroyAllWindows()

# %% ---- 2025-02-14 ------------------------
# Pending


# %% ---- 2025-02-14 ------------------------
# Pending
