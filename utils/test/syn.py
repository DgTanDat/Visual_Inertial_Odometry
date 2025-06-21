import threading
import multiprocessing 
import time
import cv2
import numpy as np
from camera import *
from imu import *
import struct
from global_interface import *
from datetime import datetime
from car_ctrl import *
import csv

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
img_dir = f"/home/dat/record/camera/"

# ==== Thread: Đọc BLE IMU ====
def ble_thread():
    imu = IMUManager(60)
    imu.imu_init()

    while True:
        time.sleep(1)  # giữ kết nối BLE sống


def get_closest_imu(ts_frame, imu_queue):
    if not imu_queue:
        return None

    closest = None
    min_diff = float("inf")

    for ts_imu, imu_data in imu_queue:
        diff = abs(ts_imu - ts_frame)
        if diff < min_diff:
            min_diff = diff
            closest = (ts_imu, imu_data)

    return closest


def car_ctrl_thread():
    controller = RobotController()
    controller.run()

def cal_angle(angle, angular_turn):
    gap = 0
    temp = abs(angle + angular_turn)
    if temp <= 180: 
        return angle + angular_turn
    else:
        gap = temp - 180
        if angular_turn < 0:
            return float(180 - gap)
        else:
            return float(-180 + gap)

def cal_distance(x0, y0, x1, y1):
    temp = ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))**(0.5)
    return temp

def write_to_csv(filepath, curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY):
    with open(filepath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY])

def imu_calculate(notifyDatas, filepath):
    global counterX, counterY, curVelX, curVelY, positionX, positionY, delta_t, init_Yaw, counter_turn, counter_forward, skip_counter
    # timeStamp   = convertData(notifyDatas, 0)
    # curRoll     = convertData(notifyDatas, 4)
    # curPitch    = convertData(notifyDatas, 8)
    curYaw      = convertData(notifyDatas, 12)
    curFaccX    = convertData(notifyDatas, 16) 
    curFaccY    = convertData(notifyDatas, 20)
    # curFaccZ    = convertData(notifyDatas, 24)
    # curWX       = convertData(notifyDatas, 28)
    # curWY       = convertData(notifyDatas, 32)
    curWZ       = convertData(notifyDatas, 36)
    if init_Yaw == None:
        init_Yaw = curYaw

    if abs(curFaccX) <= high_threadhold: #curFaccX >= (low_threadhold) and
        curFaccX = 0
        counterX += 1
    else:
        counterX = 0
    if abs(curFaccY) <= high_threadhold: #curFaccY >= (low_threadhold) and
        curFaccY = 0
        counterY += 1
    else:
        counterY = 0
    if counterX >= STABLE_THREADHOLD:
        curVelX = 0
    else:
        curVelX += (curFaccX)*delta_t
    if counterY>= STABLE_THREADHOLD:
        curVelY = 0
    else:
        curVelY += (curFaccY)*delta_t

    positionX += (curVelX)*delta_t
    positionY += (curVelY)*delta_t
    
    write_to_csv(f"{filepath}", curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY)
    
def camera_thread():
    cam = RPiCamera(640, 480, 973.3079, 973.3079, 320, 240)
    cam.PiCamera_Init()
    cam.start_camera()
    count = 0
    while True:
        timestamp, frame = cam.capture_img()
        frameName = f"{count:06d}.png"
        cv2.imwrite(f"{img_dir}/{frameName}", frame)
        count += 1

# ==== Hàm chính ====
if __name__ == "__main__":
    t1 = threading.Thread(target=camera_thread, daemon=True)
    t2 = threading.Thread(target=ble_thread, daemon=True)
    t3 = threading.Thread(target=car_ctrl_thread, daemon=True) 
    t1.start()
    t2.start()
    t3.start()
    
    # prev_time = time.time()
    # log_file = open("sync_log.txt", "w")
    # count = 0
    with open('imu.csv', 'w', newline='') as file:
        file.write("")
    while True:
        if imu_queue:
            ts_imu, data = imu_queue.popleft()
            imu_calculate(data, "imu.csv")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #     timestamp, frame = cam.capture_img()

    #     imu_data = get_closest_imu(timestamp, imu_queue)
    #     if imu_data:
    #         ts_imu, data = imu_data

    #         # Ghi vào file log
    #         imu_calculate(data, "imu.csv")
    #         log_file.write(f"{timestamp:.6f} {count:06d} {ts_imu:.6f} \n")
    #         frameName = f"{count:06d}.png"
    #         cv2.imwrite(f"{img_dir}/{frameName}", frame)
    #         count = count + 1
    #     else:
    #         imu_text = "IMU: no data"

    #     # Tính FPS
    #     now = time.time()
    #     fps = 1.0 / (now - prev_time)
    #     prev_time = now
    #     fps_text = f"FPS: {fps:.2f}"
    #     pos_text = f"Pos {positionX:0.4f} - {positionY:0.4f}"

    #     # Hiển thị overlay
    #     cv2.putText(frame, fps_text, (10, 60),
    #                 fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    #                 fontScale=0.6, color=(0, 255, 255), thickness=2)
        
    #     cv2.putText(frame, pos_text, (10, 90),
    #                 fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    #                 fontScale=0.6, color=(0, 255, 255), thickness=2)

    #     cv2.imshow("Camera + IMU", frame)

    #     # Thoát bằng phím 'q'
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cam.stop_camera()
    # log_file.close()
    t1.join()
    t2.join()
    t3.join()
    # cv2.destroyAllWindows()
        
 

