# Vision-Based Object Following Bot

A differential-drive rover that **follows a user-selected object** in real-time using computer vision. The system uses an **ESP32-CAM** for video streaming, a **Companion PC** for vision processing (YOLOv8 + CSRT tracking + PID control), and **IR sensors** for obstacle avoidance.

## Architecture

```
ESP32-CAM (MJPEG stream) → Companion PC (Python: YOLO + Tracker + PID) → ESP32/ESP8266 (Motor Control)
```

- **Detection**: YOLOv8-Nano for object detection (80 COCO classes)
- **Tracking**: OpenCV CSRT tracker with automatic re-identification on loss
- **Navigation**: Dual PID controller (angular + linear) with differential drive mapping
- **Obstacle Avoidance**: 2× IR sensors (FC-51) mounted diagonally at front corners

## Hardware Requirements

| Component | Purpose |
|-----------|---------|
| ESP32-CAM (AI Thinker) | Video streaming over Wi-Fi |
| ESP32 DevKit / ESP8266 (NodeMCU) | Motor control + IR sensor reading |
| L298N Motor Driver | Drive 2 DC motors |
| 2× DC Motors | Differential drive |
| 2× IR Obstacle Sensors (FC-51) | Diagonal front obstacle detection |
| Battery pack (7.4V–12V) | Power supply |

## Project Structure

```
├── firmware/
│   ├── esp32_cam/esp32_cam.ino          # Camera streaming firmware
│   ├── esp32_motor/esp32_motor.ino      # Motor controller (ESP32)
│   └── esp8266_motor/esp8266_motor.ino  # Motor controller (ESP8266)
├── server/
│   ├── app.py                           # Main application (OpenCV GUI)
│   ├── config.py                        # All tunable parameters
│   ├── detector.py                      # YOLOv8-Nano wrapper
│   ├── tracker.py                       # CSRT tracker + state machine
│   ├── navigator.py                     # PID controller
│   ├── obstacle_avoidance.py            # IR sensor logic
│   ├── rover_comms.py                   # HTTP comms to ESP32
│   └── frame_grabber.py                 # MJPEG stream consumer
├── models/                              # YOLO weights (auto-downloaded)
├── requirements.txt
└── testing_instructions.md
```

## Quick Start

### 1. Flash Firmware
- Upload `firmware/esp32_cam/esp32_cam.ino` to your ESP32-CAM
- Upload `firmware/esp32_motor/esp32_motor.ino` (or `esp8266_motor/`) to your motor controller
- Update Wi-Fi credentials in both sketches

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure
Edit `server/config.py` and set the IP addresses of your ESP32-CAM and motor controller.

### 4. Run
```bash
cd server
python app.py
```

### 5. Use
- **Click** on an object in the video window to select it
- **`s`** — Start following
- **`Space`** — Stop following
- **`r`** — Reselect target
- **`q`** — Quit

## PID Tuning

See [testing_instructions.md](testing_instructions.md) for detailed tuning guidance.

## License

MIT
