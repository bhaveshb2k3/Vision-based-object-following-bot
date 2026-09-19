
import cv2
import threading
import time
import requests
import numpy as np
import config


class FrameGrabber:
    def __init__(self, stream_url=config.ESP32_CAM_URL):
        self.stream_url = stream_url
        self.latest_frame = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None
        self.response = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            try:
                print(f"Connecting to camera stream at {self.stream_url}...")

                self.response = requests.get(
                    self.stream_url,
                    stream=True,
                    timeout=10
                )

                if self.response.status_code != 200:
                    print(f"Camera returned HTTP {self.response.status_code}")
                    self.response.close()
                    time.sleep(2)
                    continue

                print("Camera stream connected.")

                buffer = b""

                for chunk in self.response.iter_content(chunk_size=4096):
                    if not self.running:
                        break

                    buffer += chunk

                    start = buffer.find(b"\xff\xd8")
                    end = buffer.find(b"\xff\xd9")

                    if start != -1 and end != -1 and end > start:
                        jpg = buffer[start:end + 2]
                        buffer = buffer[end + 2:]

                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )

                        if frame is None:
                            continue

                        frame = cv2.resize(
                            frame,
                            (config.FRAME_WIDTH, config.FRAME_HEIGHT)
                        )

                        with self.lock:
                            self.latest_frame = frame

                        time.sleep(1.0 / config.FPS_TARGET)

                print("Camera stream disconnected.")

            except requests.RequestException as error:
                print(f"Camera connection error: {error}")

            except Exception as error:
                print(f"Frame grabber error: {error}")

            finally:
                if self.response:
                    self.response.close()
                    self.response = None

            if self.running:
                print("Retrying camera connection in 2 seconds...")
                time.sleep(2)

    def read(self):
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()

            return None

    def stop(self):
        self.running = False

        if self.response:
            self.response.close()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)