import os

# Network
ESP32_CAM_URL = os.getenv("ESP32_CAM_URL", "http://10.219.192.139:81/stream")
ESP32_MOTOR_URL = os.getenv("ESP32_MOTOR_URL", "http://192.168.1.101")
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Camera
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FPS_TARGET = 15

# Detection
YOLO_MODEL = "../models/yolov8n.pt"
YOLO_CONFIDENCE_THRESHOLD = 0.3
DETECTION_INTERVAL = 10          # Run YOLO every N frames

# Tracking
TRACKER_TYPE = "CSRT"            # Options: CSRT, KCF
TRACKER_CONFIDENCE_THRESHOLD = 0.3
SEARCH_TIMEOUT_SEC = 3.0

# PID — Angular (turning)
PID_ANGULAR_KP = 1.2
PID_ANGULAR_KI = 0.01
PID_ANGULAR_KD = 0.3

# PID — Linear (forward/backward)
PID_LINEAR_KP = 0.8
PID_LINEAR_KI = 0.005
PID_LINEAR_KD = 0.2

# Navigation
MAX_SPEED = 200                  # PWM max (0-255)
MIN_SPEED = 60                   # Below this, motors stall
DEAD_ZONE = 0.05                 # Error threshold to ignore
TARGET_BBOX_RATIO = 0.15         # Target should occupy ~15% of frame

# Obstacle Avoidance (IR sensors — digital, no distance value)
IR_DEBOUNCE_MS = 50              # Ignore flickers shorter than this
OBSTACLE_STEER_FACTOR = 0.7      # How aggressively to steer away (0-1)
BOTH_BLOCKED_TIMEOUT_SEC = 5.0   # Notify app after blocked this long

# Safety
WATCHDOG_TIMEOUT_MS = 500        # Stop if no command in this time
