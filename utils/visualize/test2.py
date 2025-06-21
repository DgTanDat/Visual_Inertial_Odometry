import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import tqdm
from visual_odometry import PinholeCamera, VisualOdometry

# Hàm đọc thông số camera từ calib.txt
def read_calib_file(calib_path):
    with open(calib_path, 'r') as f:
        for line in f:
            if line.startswith('P0:'):
                params = [float(x) for x in line.split()[1:]]
                fx, cx, fy, cy = params[0], params[2], params[4], params[5]
                return fx, fy, cx, cy
    raise ValueError("P0 not found in calib.txt")

# Hàm đọc ground truth từ file poses/XX.txt
def read_ground_truth(annotations_path):
    ground_truth = []
    with open(annotations_path, 'r') as f:
        for line in f:
            params = [float(x) for x in line.strip().split()]
            x, y, z = params[3], params[7], params[11]  # tx, ty, tz
            ground_truth.append([x, y, z])
    return np.array(ground_truth)

# Đường dẫn đến sequence 01
base_path = '/home/dat/record/camera/2025-06-11_22-01-17/'#'/home/dat/Downloads/06/image_0/'
annotations = "/home/dat/Downloads/06/poses.txt"
calib_path = "/home/dat/Downloads/10/calib.txt"

# Kiểm tra file tồn tại
if not os.path.exists(base_path):
    raise FileNotFoundError(f"Directory {base_path} not found")
if not os.path.exists(annotations):
    raise FileNotFoundError(f"Ground truth file {annotations} not found")
if not os.path.exists(calib_path):
    raise FileNotFoundError(f"Calibration file {calib_path} not found")

# Đọc thông số camera
fx, fy, cx, cy = read_calib_file(calib_path)
# Kiểm tra kích thước hình ảnh
sample_img = cv2.imread(os.path.join(base_path, "000000.png"), cv2.IMREAD_GRAYSCALE)
if sample_img is None:
    raise ValueError("Failed to load sample image")
height, width = sample_img.shape

# Khởi tạo camera
# cam = PinholeCamera(1241.0, 376.0, 718.8560, 718.8560, 620.5, 188.0)
cam = PinholeCamera(640, 480, 973.3079, 973.3079, 320, 240)
# cam = PinholeCamera(1226.0, 370.0, 718.8560, 718.8560, 607.1928, 185.2157)
# cam = PinholeCamera(1226.0, 370.0, 707.0912, 707.0912, 601.8873, 183.1104)
# Khởi tạo Visual Odometry
vo = VisualOdometry(cam)

# Đếm số frame
num_frames = len([f for f in os.listdir(base_path) if f.endswith('.png')])
print(f"Processing {num_frames} frames in sequence 01")

# Lưu quỹ đạo
traj = []
ground_truth = read_ground_truth(annotations)
# Xử lý từng frame
# for img_id in range(num_frames):
for img_id in tqdm.tqdm(range(num_frames), desc="Processing frames", ncols=100):
    img_path = os.path.join(base_path, f"{img_id:06d}.png")
    if not os.path.exists(img_path):
        print(f"Error: File {img_path} does not exist")
        continue
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Failed to load image {img_path}")
        continue
    vo.update(img, 0.02)
    if vo.cur_t is not None:
        traj.append(vo.cur_t.flatten())
        # print(f"Frame {img_id}: t = {vo.cur_t.flatten()}")

# Vẽ quỹ đạo
traj = np.array(traj)
plt.plot(traj[:, 2], traj[:, 0], label="Estimated")
# plt.plot(ground_truth[:, 0], ground_truth[:, 2], 'r--', label="Ground Truth")
plt.xlabel("X")
plt.ylabel("Z")
plt.legend()
plt.grid()
plt.show()