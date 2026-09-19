import config

class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

class Navigator:
    def __init__(self):
        self.pid_angular = PID(config.PID_ANGULAR_KP, config.PID_ANGULAR_KI, config.PID_ANGULAR_KD)
        self.pid_linear = PID(config.PID_LINEAR_KP, config.PID_LINEAR_KI, config.PID_LINEAR_KD)

    def compute_speeds(self, bbox):
        """
        Computes left and right motor speeds based on tracking bounding box.
        bbox format: (x, y, w, h)
        """
        if not bbox:
            return 0, 0

        x, y, w, h = bbox
        
        # Calculate horizontal error (-1 to 1)
        center_x = x + w / 2
        frame_center_x = config.FRAME_WIDTH / 2
        horizontal_error = (center_x - frame_center_x) / (config.FRAME_WIDTH / 2)
        
        # Dead zone for angular
        if abs(horizontal_error) < config.DEAD_ZONE:
            horizontal_error = 0

        # Calculate size error for linear speed
        current_ratio = (w * h) / (config.FRAME_WIDTH * config.FRAME_HEIGHT)
        size_error = config.TARGET_BBOX_RATIO - current_ratio
        
        # Dead zone for linear
        if abs(size_error) < config.DEAD_ZONE * 0.5:
            size_error = 0

        angular_vel = self.pid_angular.compute(horizontal_error) * config.MAX_SPEED
        linear_vel = self.pid_linear.compute(size_error) * config.MAX_SPEED

        # Differential drive mapping
        left_speed = linear_vel + angular_vel
        right_speed = linear_vel - angular_vel

        # Add minimum speed offset if non-zero
        if left_speed > 0: left_speed += config.MIN_SPEED
        elif left_speed < 0: left_speed -= config.MIN_SPEED
            
        if right_speed > 0: right_speed += config.MIN_SPEED
        elif right_speed < 0: right_speed -= config.MIN_SPEED

        # Constrain
        left_speed = max(min(int(left_speed), config.MAX_SPEED), -config.MAX_SPEED)
        right_speed = max(min(int(right_speed), config.MAX_SPEED), -config.MAX_SPEED)

        return left_speed, right_speed
