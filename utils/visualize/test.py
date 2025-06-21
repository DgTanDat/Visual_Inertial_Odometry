import pandas as pd
import matplotlib.pyplot as plt

# Tên các cột theo thứ tự
column_names = ['curFaccX', 'curFaccY', 'curYaw', 'curWZ', 'curVelX', 'curVelY', 'positionX', 'positionY', 'initYaw']

# Đọc dữ liệu CSV không có header
file_path = '/home/dat/record/imu/2025-06-11_19-43-59.csv'  # Thay bằng đường dẫn thật
df = pd.read_csv(file_path, header=None, names=column_names)

# Trích xuất dữ liệu vị trí
x = df['positionX'].values
y = df['positionY'].values

# Vẽ biểu đồ
plt.figure(figsize=(8, 8))
plt.plot(x, y, color='blue', linewidth=2, label='Path')
plt.scatter(x[0], y[0], color='green', s=50, label='Start')
plt.scatter(x[-1], y[-1], color='red', s=50, label='End')

plt.xlabel('Position X')
plt.ylabel('Position Y')
plt.title('Path Visualization')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()
