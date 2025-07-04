import socketio
import time
import mss
import cv2
import numpy as np
import base64
import threading

sio = socketio.Client()
streaming = False

@sio.event(namespace='/client')
def connect():
    print("✅ Agent connected and waiting...")

@sio.on('start_stream', namespace='/client')
def start_stream(data):
    global streaming
    if not streaming:
        print("📡 Starting stream...")
        streaming = True
        threading.Thread(target=send_frames, daemon=True).start()
@sio.on('stop_stream', namespace='/client')
def stop_stream(data):
    global streaming
    print("🛑 Stopping stream...")
    streaming = False
    
def send_frames():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while streaming:
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
            encoded = base64.b64encode(buffer).decode('utf-8')

            sio.emit('frame', {'image': encoded}, namespace='/client')
            time.sleep(0.3)  # ~3 FPS

sio.connect('http://192.168.1.27:5005', namespaces=['/client'])
sio.wait()
