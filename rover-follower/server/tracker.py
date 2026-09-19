import cv2
import time
import config

class Tracker:
    def __init__(self):
        self.state = "IDLE" # IDLE, TRACKING, SEARCHING
        self.tracker = None
        self.target_class = None
        self.last_seen_time = 0
        self.bbox = None # (x, y, w, h)
        
    def init_tracker(self, frame, bbox, target_class):
        if config.TRACKER_TYPE == "CSRT":
            self.tracker = cv2.TrackerCSRT_create()
        else:
            self.tracker = cv2.TrackerKCF_create()
            
        self.tracker.init(frame, bbox)
        self.target_class = target_class
        self.bbox = bbox
        self.state = "TRACKING"
        self.last_seen_time = time.time()
        print(f"Started tracking: {target_class} at {bbox}")

    def update(self, frame):
        if self.state != "TRACKING":
            return False, None

        success, bbox = self.tracker.update(frame)
        if success:
            self.bbox = tuple(map(int, bbox))
            self.last_seen_time = time.time()
            return True, self.bbox
        else:
            self.state = "SEARCHING"
            print("Tracker lost object. Searching...")
            return False, None

    def handle_search(self, detections):
        """
        Called when in SEARCHING state to try to re-identify the object based on YOLO detections.
        """
        if self.state != "SEARCHING":
            return False

        if time.time() - self.last_seen_time > config.SEARCH_TIMEOUT_SEC:
            self.state = "IDLE"
            self.target_class = None
            self.bbox = None
            print("Search timeout. Returning to IDLE.")
            return False

        # Simple re-identification: match the target class with the highest confidence detection
        best_match = None
        highest_conf = 0
        for det in detections:
            if det['class'] == self.target_class and det['confidence'] > highest_conf:
                best_match = det
                highest_conf = det['confidence']
                
        if best_match:
            print(f"Re-identified {self.target_class}. Resuming tracking.")
            return best_match['bbox']
            
        return False
