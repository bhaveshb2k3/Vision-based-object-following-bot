from ultralytics import YOLO
import config

class Detector:
    def __init__(self, model_path=config.YOLO_MODEL):
        try:
            self.model = YOLO(model_path)
            print(f"Loaded YOLO model from {model_path}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = YOLO("yolov8n.pt") # Fallback to download

    def detect(self, frame):
        """
        Runs inference on a single frame.
        Returns a list of dicts: [{'class': name, 'confidence': conf, 'bbox': (x, y, w, h)}]
        """
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                
                # Debug output
                print(f"YOLO saw: {cls_name} at {conf:.2f} confidence")
                
                if conf >= config.YOLO_CONFIDENCE_THRESHOLD:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    # x1, y1, x2, y2 format from YOLO, convert to x, y, w, h
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w = x2 - x1
                    h = y2 - y1
                    detections.append({
                        'class': cls_name,
                        'confidence': conf,
                        'bbox': (x1, y1, w, h)
                    })
        return detections

    def get_nearest_detection(self, detections, tap_x, tap_y, frame_w, frame_h):
        """
        Finds the detection whose center is closest to the normalized tap coordinates.
        """
        if not detections:
            return None
            
        target_x = int(tap_x * frame_w)
        target_y = int(tap_y * frame_h)
        
        best_det = None
        min_dist = float('inf')
        
        for det in detections:
            x, y, w, h = det['bbox']
            center_x = x + w / 2
            center_y = y + h / 2
            
            dist = (center_x - target_x)**2 + (center_y - target_y)**2
            if dist < min_dist:
                min_dist = dist
                best_det = det
                
        return best_det
