import config
import time

class ObstacleAvoidance:
    def __init__(self):
        self.left_blocked = False
        self.right_blocked = False
        self.both_blocked_start = 0

    def update_sensor_state(self, left, right):
        self.left_blocked = left
        self.right_blocked = right
        
        if self.left_blocked and self.right_blocked:
            if self.both_blocked_start == 0:
                self.both_blocked_start = time.time()
        else:
            self.both_blocked_start = 0

    def apply(self, left_speed, right_speed):
        """
        Modifies intended motor speeds based on IR sensor flags.
        Returns: (modified_left_speed, modified_right_speed, alert_message)
        """
        alert = None

        if self.left_blocked and self.right_blocked:
            # Full stop
            left_speed, right_speed = 0, 0
            if time.time() - self.both_blocked_start > config.BOTH_BLOCKED_TIMEOUT_SEC:
                alert = "Path completely blocked!"
        elif self.left_blocked and not self.right_blocked:
            # Steer right (reduce left motor speed or reverse it)
            left_speed = int(left_speed * (1.0 - config.OBSTACLE_STEER_FACTOR))
            # Boost right motor slightly to help turn
            right_speed = int(right_speed * (1.0 + config.OBSTACLE_STEER_FACTOR/2))
            alert = "Obstacle on left, steering right"
        elif self.right_blocked and not self.left_blocked:
            # Steer left (reduce right motor speed or reverse it)
            right_speed = int(right_speed * (1.0 - config.OBSTACLE_STEER_FACTOR))
            # Boost left motor slightly to help turn
            left_speed = int(left_speed * (1.0 + config.OBSTACLE_STEER_FACTOR/2))
            alert = "Obstacle on right, steering left"
            
        # Ensure we don't exceed max speed after boosting
        left_speed = max(min(left_speed, config.MAX_SPEED), -config.MAX_SPEED)
        right_speed = max(min(right_speed, config.MAX_SPEED), -config.MAX_SPEED)

        return left_speed, right_speed, alert
