import pandas as pd
import matplotlib.pyplot as plt

# Đường dẫn đến 2 file CSV
file_day_du = '/home/dat/record/imu/2025-06-21_12-29-11.csv'
file_3_cot = '/home/dat/record/raw_imu/2025-06-21_12-29-11.csv'

# Tên cột cho từng file
cols_full = ['curFaccX', 'curFaccY', 'curYaw', 'curWZ', 'curVelX', 'curVelY', 'positionX', 'positionY', 'initYaw']
cols_partial = ['curFaccX', 'curFaccY', 'curYaw']

# Đọc file không có tiêu đề
df_full = pd.read_csv(file_day_du, header=None, names=cols_full)
df_partial = pd.read_csv(file_3_cot, header=None, names=cols_partial)

# Cắt dữ liệu đến độ dài nhỏ nhất để tránh lỗi
min_len = min(len(df_full), len(df_partial))
df_full = df_full.iloc[:min_len]
df_partial = df_partial.iloc[:min_len]

# Các cột cần so sánh
columns_to_compare = ['curFaccX', 'curFaccY', 'curYaw']

# Vẽ biểu đồ so sánh từng cột
plt.figure(figsize=(12, 8))

for i, col in enumerate(columns_to_compare, start=1):
    plt.subplot(3, 1, i)
    plt.plot(df_full[col], label=f'{col} - file đầy đủ')
    plt.plot(df_partial[col], label=f'{col} - file 3 cột', linestyle='--')
    plt.title(f'So sánh giá trị {col}')
    plt.xlabel('Thời gian (dòng)')
    plt.ylabel(col)
    plt.legend()
    plt.grid(True)

plt.tight_layout()
plt.show()
