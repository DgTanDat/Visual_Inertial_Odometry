import numpy as np
import math

class Filter:
    def __init__(self, alpha=0.5):
        # Trạng thái: [x, y, theta]
        self.state = np.zeros(2)
        # Trọng số (alpha gần 1 ưu tiên VO, gần 0 ưu tiên IMU)
        self.alpha = alpha

    def update(self, vo_t, imu_t):
        """
        Cập nhật trạng thái dùng VO ([t, R]) và IMU ([x, y, yaw]).
        vo_t: translation vector [tx, ty]
        vo_R: rotation matrix 2x2
        imu_state: [x, y, yaw] từ IMU
        """

        # Kết hợp với IMU (tham chiếu dài hạn)
        self.state = self.alpha * vo_t + (1 - self.alpha) * imu_t

        return self.state

