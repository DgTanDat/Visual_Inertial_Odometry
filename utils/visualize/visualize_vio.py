import csv
import matplotlib.pyplot as plt

# Đọc file CSV
x_values = []
y_values = []

with open('/home/dat/record/vio/2025-06-21_12-50-14.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            try:
                x = float(row[0])
                y = float(row[1])
                x_values.append(x)
                y_values.append(y)
            except ValueError:
                # Bỏ qua dòng không hợp lệ
                continue

# Vẽ đồ thị
plt.plot(x_values, y_values, marker='o')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Biểu đồ từ file CSV')
plt.grid(True)
plt.show()
