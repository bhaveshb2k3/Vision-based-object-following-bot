import requests
import config
import threading

class RoverComms:
    def __init__(self, base_url=config.ESP32_MOTOR_URL):
        self.base_url = base_url
        self.last_left = 0
        self.last_right = 0
        
    def send_command(self, left_speed, right_speed):
        """
        Sends motor speeds to the ESP32. Avoids sending duplicates to save bandwidth.
        """
        if left_speed == self.last_left and right_speed == self.last_right:
            return # No change
            
        self.last_left = left_speed
        self.last_right = right_speed
        
        # Fire and forget in a background thread to avoid blocking the vision loop
        threading.Thread(target=self._post_command, args=(left_speed, right_speed), daemon=True).start()

    def _post_command(self, left, right):
        try:
            url = f"{self.base_url}/control?left={left}&right={right}"
            requests.get(url, timeout=0.2)
        except requests.exceptions.RequestException:
            pass # Ignore connection errors to prevent log spam if rover disconnects
            
    def get_status(self):
        """
        Polls the ESP32 for IR sensor status.
        """
        try:
            url = f"{self.base_url}/status"
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
