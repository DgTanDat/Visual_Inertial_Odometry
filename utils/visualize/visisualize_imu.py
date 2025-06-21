import pandas as pd
import matplotlib.pyplot as plt

# Tên cột theo thứ tự file CSV
column_names = ['curFaccX', 'curFaccY', 'curYaw', 'curWZ', 'curVelX', 'curVelY', 'positionX', 'positionY', 'initYaw']

# Đọc dữ liệu từ CSV không có tiêu đề
df = pd.read_csv('/home/dat/record/imu/2025-06-21_12-50-14.csv', header=None, names=column_names)

# Tạo 2x2 subplot (4 ô vuông)
fig, axs = plt.subplots(2, 2, figsize=(10, 10))  # chỉnh figsize để vuông

fig.suptitle('AccX, AccY, Yaw và Quỹ đạo', fontsize=16)

# 1. Acc X
axs[0, 0].plot(df['curFaccX'], color='blue')
axs[0, 0].set_title('Acc X')
axs[0, 0].grid(True)


# 2. Acc Y
axs[0, 1].plot(df['curFaccY'], color='green')
axs[0, 1].set_title('Acc Y')
axs[0, 1].grid(True)


# 3. Yaw
axs[1, 0].plot(df['curYaw'], color='red')
axs[1, 0].set_title('Yaw')
axs[1, 0].grid(True)


# 4. Quỹ đạo vị trí (posX vs posY)
axs[1, 1].plot(df['positionX'], df['positionY'], color='purple', marker='o')
axs[1, 1].set_title('Quỹ đạo Odometry')
axs[1, 1].grid(True)


plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
