import cv2
import time
import sys
import threading
import config
from frame_grabber import FrameGrabber
from detector import Detector
from tracker import Tracker
from navigator import Navigator
from obstacle_avoidance import ObstacleAvoidance
from rover_comms import RoverComms

class RoverApp:
    def __init__(self):
        print("Initializing systems...")
        self.grabber = FrameGrabber()
        self.detector = Detector()
        self.tracker = Tracker()
        self.navigator = Navigator()
        self.obstacle = ObstacleAvoidance()
        self.comms = RoverComms()
        
        self.is_following = False
        self.window_name = "Rover Control"
        self.alert_message = ""
        self.alert_time = 0
        self.frame_count = 0
        self.latest_detections = []
        
    def show_alert(self, message):
        self.alert_message = message
        self.alert_time = time.time()
        print(f"ALERT: {message}")

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            frame = self.grabber.read()
            if frame is None:
                return
                
            # Normalize coordinates
            norm_x = x / config.FRAME_WIDTH
            norm_y = y / config.FRAME_HEIGHT
            
            detections = self.detector.detect(frame)
            best_det = self.detector.get_nearest_detection(detections, norm_x, norm_y, config.FRAME_WIDTH, config.FRAME_HEIGHT)
            
            if best_det:
                self.tracker.init_tracker(frame, best_det['bbox'], best_det['class'])
                self.is_following = True
                self.show_alert(f"Selected {best_det['class']}")
            else:
                self.show_alert("No object detected near click")

    def draw_ui(self, frame):
        # Base UI overlay
        cv2.putText(frame, "Controls: [S]tart  [Space]Stop  [R]eselect  [Q]uit", (10, config.FRAME_HEIGHT - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # State
        state_text = f"State: {self.tracker.state if self.is_following else 'IDLE'}"
        color = (0, 255, 0) if self.tracker.state == "TRACKING" else (0, 165, 255)
        if not self.is_following: color = (255, 255, 255)
        cv2.putText(frame, state_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Obstacle indicators
        if self.obstacle.left_blocked:
            cv2.putText(frame, "WARN L", (10, config.FRAME_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if self.obstacle.right_blocked:
            cv2.putText(frame, "WARN R", (config.FRAME_WIDTH - 70, config.FRAME_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
        # Target bounding box
        if self.tracker.bbox and self.tracker.state == "TRACKING":
            bx, by, bw, bh = self.tracker.bbox
            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
            
        # Alert box
        if time.time() - self.alert_time < 3.0 and self.alert_message:
            cv2.putText(frame, self.alert_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)
        
        self.grabber.start()
        print("Ready. Video stream starting...")
        
        try:
            while True:
                frame = self.grabber.read()
                if frame is None:
                    time.sleep(0.01)
                    continue
                    
                self.frame_count += 1
                
                # 1. Update obstacles
                status = self.comms.get_status()
                if status:
                    self.obstacle.update_sensor_state(status.get("left_blocked", False), status.get("right_blocked", False))
                
                # 2. Tracking & Navigation
                if self.is_following:
                    if self.tracker.state == "TRACKING":
                        success, bbox = self.tracker.update(frame)
                        if not success:
                            self.show_alert("Target lost, searching...")
                            self.comms.send_command(0, 0)
                        else:
                            if self.frame_count % config.DETECTION_INTERVAL == 0:
                                self.latest_detections = self.detector.detect(frame)
                                self.tracker.handle_search(self.latest_detections)
                            
                            left_s, right_s = self.navigator.compute_speeds(bbox)
                            left_s, right_s, obs_alert = self.obstacle.apply(left_s, right_s)
                            
                            if obs_alert: self.show_alert(obs_alert)
                            self.comms.send_command(left_s, right_s)
                            
                    elif self.tracker.state == "SEARCHING":
                        self.latest_detections = self.detector.detect(frame)
                        new_bbox = self.tracker.handle_search(self.latest_detections)
                        if new_bbox:
                            self.tracker.init_tracker(frame, new_bbox, self.tracker.target_class)
                            self.show_alert(f"Found {self.tracker.target_class} again")
                        elif self.tracker.state == "IDLE":
                            self.is_following = False
                            self.comms.send_command(0, 0)
                            self.show_alert("Search timeout. Tracking stopped.")
                else:
                    self.comms.send_command(0, 0)

                # 3. Render
                self.draw_ui(frame)
                cv2.imshow(self.window_name, frame)
                
                # 4. Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if self.tracker.target_class:
                        self.is_following = True
                        self.show_alert("Tracking STARTED")
                elif key == ord(' '):
                    self.is_following = False
                    self.show_alert("Tracking STOPPED")
                elif key == ord('r'):
                    self.is_following = False
                    self.tracker.state = "IDLE"
                    self.tracker.target_class = None
                    self.tracker.bbox = None
                    self.show_alert("Target cleared. Click to select new.")
                    
                time.sleep(1.0 / config.FPS_TARGET)
                
        finally:
            print("Shutting down...")
            self.comms.send_command(0, 0)
            self.grabber.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = RoverApp()
    app.run()
