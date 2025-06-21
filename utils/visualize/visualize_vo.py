import matplotlib.pyplot as plt
import csv

# Khởi tạo danh sách để lưu các giá trị posX và posZ
posX = []
posZ = []

# Mở file CSV có dữ liệu dạng [x y z]
with open('/home/dat/record/vo/2025-06-21_12-50-14.csv', 'r') as f:
    for line in f:
        # line = line.strip().strip('[]')  # loại bỏ dấu [] và khoảng trắng đầu-cuối
        if line:
            parts = line.split(",")  # tách theo khoảng trắng
            if len(parts) == 3:
                x, y, z = map(float, parts)
                posX.append(x)
                posZ.append(z)
# with open('vo.csv', 'r') as f:
#     csvreader = csv.reader('vo.csv')
#     fields = next(csvreader)
#     for row in csvreader: 
#         posX.append(float(row[0]))
#         posZ.append(float(row[2]))
        
neg = [-x for x in posX]
# Vẽ biểu đồ 2D với posX và posZ
# plt.figure(figsize=(8, 6))
plt.plot(posZ, neg, marker='o', linestyle='-')
plt.title('Plot posX vs posZ')
plt.xlabel('posX')
plt.ylabel('posZ')
plt.grid(True)
plt.axis('equal')
plt.show()
