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

scale_image_for_yolo_speed_up = 2

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
            image=mat[::scale_image_for_yolo_speed_up, ::scale_image_for_yolo_speed_up, :].copy(), return_detections=True)


def assign_points(p1, p2, p3):
    '''
    Assign the points.

    The right most point as NE.
    The other two points on the top, as the NW.
    The latest point as the SW.
    '''
    points = np.array([p1, p2, p3])
    p_ne = sorted(points, key=lambda p: p[0], reverse=True)[0]
    points = [e for e in points if np.sum(np.abs(e-p_ne)) != 0]

    if points[0][1] > points[1][1]:
        p_sw = points[0]
        p_nw = points[1]
    else:
        p_sw = points[1]
        p_nw = points[0]

    corner_points = {
        'NE': p_ne,
        'NW': p_nw,
        'SW': p_sw,
    }
    return corner_points


def convert_coordinates(corner_points, point):
    '''
    Convert the point to the coordinate system defined by the corner points.
    The NE point's coordinates are (1, 0).
    The NW point's coordinates are (0, 0).
    The SW point's coordinates are (0, 1).
    '''
    point = np.array(point)
    nw = corner_points['NW']
    ne = corner_points['NE']
    sw = corner_points['SW']
    u = point - nw
    g1 = ne - nw
    g2 = sw - nw
    f1 = np.array([g2[1], -g2[0]])
    h1 = f1 / np.dot(g1, f1)
    f2 = np.array([g1[1], -g1[0]])
    h2 = f2 / np.dot(g2, f2)
    x, y = np.dot(u, h1), np.dot(u, h2)
    return x, y


def guess_gaze_xy_in_screen(found, fx, fy):
    p1 = np.array(found[1][0]['cxcy'])*scale_image_for_yolo_speed_up
    p2 = np.array(found[1][1]['cxcy'])*scale_image_for_yolo_speed_up
    p3 = np.array(found[1][2]['cxcy'])*scale_image_for_yolo_speed_up
    corner_points = assign_points(p1, p2, p3)
    x, y = convert_coordinates(corner_points, (fx, fy))
    return x, y


threading.Thread(target=detect_qrcode, daemon=True).start()

# %% ---- 2025-02-14 ------------------------
# Play ground
cv2.namedWindow(winname)
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
        # print(f['cxcy'])
        x, y = f['cxcy']
        x *= scale_image_for_yolo_speed_up
        y *= scale_image_for_yolo_speed_up
        mat[int(y)-10:int(y)+10, int(x)-10:int(x)+10] = (0, 255, 0)

    fx = int(fx * w)
    fy = int(fy * h)

    mat[fy-10:fy+10, fx-10:fx+10, 2] = 255

    try:
        _x, _y = guess_gaze_xy_in_screen(found, fx, fy)
        print(f'Estimated gaze coord: {_x:0.2f}, {_y:0.2f}')
    except:
        import traceback
        traceback.print_exc()
        pass

    cv2.imshow(winname, mat)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# %% ---- 2025-02-14 ------------------------
# Pending


# %% ---- 2025-02-14 ------------------------
# Pending
