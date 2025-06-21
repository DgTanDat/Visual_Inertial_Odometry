import numpy as np
from filterpy.kalman import ExtendedKalmanFilter
from filterpy.common import Q_discrete_white_noise
import math

# Define the EKF class for a 4WD skid-steering vehicle combining IMU and camera data
class SkidSteerEKF(ExtendedKalmanFilter):
    def __init__(self, dt):
        # Initialize EKF: state vector [x, y, theta] (position x, y, heading)
        super().__init__(dim_x=3, dim_z=3)  # dim_x: state, dim_z: measurement
        self.dt = dt  # Time step

        # Initial state: [x, y, theta]
        self.x = np.zeros((3, 1))

        # Initial covariance matrix (uncertainty in state)
        self.P = np.eye(3) * 1.0  # Start with moderate uncertainty

        # Process noise covariance (tune these values based on system)
        # var_process = 0.1  # Process noise variance
        # self.Q = Q_discrete_white_noise(dim=2, dt=dt, var=var_process)
        # self.Q = np.block([[self.Q, np.zeros((2, 1))],
        #                   [np.zeros((1, 2)), var_process * dt]])  # Expand to 3x3 for [x, y, theta]
        self.Q = np.diag([0.01, 0.01, 0.005])
        # Measurement noise covariance (tune based on IMU and camera accuracy)
        self.R = np.diag([0.1, 0.1, 0.05])  # [x, y from camera, theta from IMU]

    def predict(self, u):
        """
        Predict next state based on control input u = [v_cmd, omega_cmd]
        v_cmd: commanded velocity (m/s)
        omega_cmd: commanded angular velocity (rad/s) for skid-steering
        """
        theta = self.x[2, 0]  # Current heading
        v_cmd, omega_cmd = u  # Control inputs

        # Simple skid-steering motion model
        # x' = x + v_cmd * cos(theta) * dt
        # y' = y + v_cmd * sin(theta) * dt
        # theta' = theta + omega_cmd * dt
        x_new = self.x[0, 0] + v_cmd * math.cos(theta) * self.dt
        y_new = self.x[1, 0] + v_cmd * math.sin(theta) * self.dt
        theta_new = self.x[2, 0] + omega_cmd * self.dt

        # Update state
        self.x = np.array([[x_new], [y_new], [theta_new]])

        # Jacobian of the motion model (F matrix)
        self.F = np.array([[1, 0, -v_cmd * math.sin(theta) * self.dt],
                           [0, 1, v_cmd * math.cos(theta) * self.dt],
                           [0, 0, 1]])

        # Standard EKF predict step
        super().predict()

    def update(self, z):
        """
        Update step with measurements z = [x_cam, y_cam, theta_imu]
        x_cam, y_cam: position from camera (m)
        theta_imu: heading from IMU (radians)
        """
        def HJacobian(x):
            # Jacobian of measurement model (H matrix)
            # Measurement model: z = [x, y, theta] + noise
            return np.eye(3)  # Linear mapping for simplicity

        def Hx(x):
            # Measurement function: maps state to measurement space
            return x  # Direct mapping for [x, y, theta]

        # Standard EKF update step
        super().update(z, HJacobian, Hx)

# Example usage
def main():
    dt = 0.1  # Time step (s)
    ekf = SkidSteerEKF(dt)

    # Simulated control inputs (commanded velocity, angular velocity)
    u = [1.0, 0.2]  # [v_cmd = 1.0 m/s, omega_cmd = 0.2 rad/s]

    # Simulated measurements [x_cam, y_cam, theta_imu]
    # Add noise to simulate real sensor data
    z = np.array([[0.11],  # x from camera with slight noise
                  [0.09],  # y from camera with slight noise
                  [0.02]]) # theta from IMU with slight noise

    # Main loop
    for i in range(10):  # Run for 10 steps
        # Predict step
        ekf.predict(u)
        print(f"Step {i+1} - Predicted state: x={ekf.x[0,0]:.2f}, y={ekf.x[1,0]:.2f}, "
              f"theta={ekf.x[2,0]:.2f}")

        # Update step with measurements
        ekf.update(z)
        print(f"Step {i+1} - Updated state: x={ekf.x[0,0]:.2f}, y={ekf.x[1,0]:.2f}, "
              f"theta={ekf.x[2,0]:.2f}")

        # Simulate new measurements (in practice, get from real IMU and camera)
        z += np.array([[0.1], [0.1], [0.02]])  # Simple increment for demo

if __name__ == "__main__":
    main()