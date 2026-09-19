# Integration Testing & PID Tuning Guide

## 1. Hardware Verification
1. **Flash ESP32-CAM**: Upload `firmware/esp32_cam/esp32_cam.ino`. 
   - Open Serial Monitor, note the IP address.
   - Verify stream works by navigating to `http://<IP>:81/stream` in your browser.
2. **Flash Motor Controller**: Upload `firmware/esp32_motor/esp32_motor.ino` (if using ESP32) or `firmware/esp8266_motor/esp8266_motor.ino` (if using ESP8266).
   - Open Serial Monitor, note the IP address.
   - Test IR sensors: Block the left and right IR sensors. Navigating to `http://<IP>/status` should show `left_blocked: true` / `right_blocked: true`.
   - Test Motors: Navigate to `http://<IP>/control?left=150&right=150`. Motors should spin forward for 500ms then stop (watchdog kicks in).

## 2. Software Setup
1. Open `server/config.py`.
2. Update `ESP32_CAM_URL` and `ESP32_MOTOR_URL` with the actual IP addresses from step 1.
3. Install Python dependencies: `pip install -r requirements.txt`
4. Start the app: `cd server && python app.py`
   - *Note: On the first run, the Ultralytics library will automatically download the YOLOv8-Nano model weights (`yolov8n.pt`) if they aren't already present in your directory.*
5. A window named **Rover Control** will open showing the camera stream.

## 3. End-to-End Test
1. Have someone stand in front of the rover.
2. Click on the person in the video feed using your mouse. A bounding box should appear and the state should change to `IDLE` (with target selected).
3. Press **`s`** on your keyboard to start. The state will change to `TRACKING` and the rover should begin following the person.
4. Press the **Spacebar** to stop following.
5. Press **`r`** to reselect a target.
6. Press **`q`** to quit the app.


## 4. PID Tuning
If the rover behavior is erratic, adjust the PID constants in `server/config.py`:

**Erratic Turning (Oscillation left/right):**
- Decrease `PID_ANGULAR_KP` (e.g., from 1.2 to 0.8)
- Increase `PID_ANGULAR_KD` slightly (e.g., from 0.3 to 0.5) to dampen oscillations.

**Slow to Turn:**
- Increase `PID_ANGULAR_KP` (e.g., from 1.2 to 1.5).

**Erratic Forward/Backward Movement (Jerky speed):**
- Decrease `PID_LINEAR_KP`.

**Stops too far away / Gets too close:**
- Adjust `TARGET_BBOX_RATIO`. A larger ratio means it will get closer before stopping.

## 5. Obstacle Avoidance Tuning
- Use a screwdriver to turn the potentiometers on the FC-51 IR sensors. Set them so they trigger at roughly 20-30cm distance.
- Adjust `OBSTACLE_STEER_FACTOR` in `config.py` if the rover doesn't steer sharply enough when an obstacle is detected.
