from multiprocessing import Process
from threading import Thread
import time
import struct
from interface.global_interface import *
from datetime import datetime
import csv
import cv2
import os
from src.camera.camera import *
from src.imu.imu import *
from src.motor.car_ctrl import *
from src.camera.visual_odometry import PinholeCamera, VisualOdometry

file_lock = threading.Lock()
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
img_dir = f"/home/dat/record/camera/{current_datetime}"
imu_dir = f"/home/dat/record/imu/{current_datetime}.csv"
vo_dir = f"/home/dat/record/vo/{current_datetime}.csv"
vio_dir = f"/home/dat/record/vio/{current_datetime}.csv"
alpha = 0.7
# def get_closest_imu(ts_frame, imu_queue):
#     if not imu_queue:
#         return None

#     closest = None
#     min_diff = float("inf")

#     for ts_imu, imu_data in imu_queue:
#         diff = abs(ts_imu - ts_frame)
#         if diff < min_diff:
#             min_diff = diff
#             closest = (ts_imu, imu_data)

#     return closest

def cal_distance(x0, y0, x1, y1):
    temp = ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))**(0.5)
    return temp

def write_to_csv(filepath, curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY, init_Yaw):
    with open(filepath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY, init_Yaw])

def imu_calculate(notifyDatas, filepath):
    global counterX, counterY, curVelX, curVelY, positionX, positionY, delta_t, init_Yaw, last_Yaw, counter_turn, counter_forward, timer_wait_stable
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

    with open("raw_imu.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([curFaccX, curFaccY, curYaw])

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

    if int(last_Yaw) != int(curYaw):
        counter_turn += 1
        counter_forward = 0
    else:
        counter_forward += 1
        if counter_forward >= 10:
            counter_turn = 0

    if(counter_turn >= 10):
        timer_wait_stable = 15

    if timer_wait_stable > 0:
        curFaccX = 0
        curFaccY = 0
        curVelX = 0
        curVelY = 0
        timer_wait_stable -= 1
    
    positionX += (curVelX)*delta_t
    positionY += (curVelY)*delta_t
    last_Yaw = curYaw
    write_to_csv(f"{filepath}", curFaccX, curFaccY, curYaw, curWZ, curVelX, curVelY, positionX, positionY, init_Yaw)
    return positionX, positionY, (curYaw - init_Yaw)

def ble_thread():
    with open('raw_imu.csv', 'w', newline='') as file:
        file.write("")
    imu = IMUManager(30)
    imu.imu_init()

    while True:
        time.sleep(1)  # giữ kết nối BLE sống

def car_ctrl_thread():
    controller = RobotController(file_lock)
    controller.run()

def vio_thread():
    # store last imu and cur imu
    last_x_imu = 0
    last_y_imu = 0
    last_theta_imu = 0
    cam = PinholeCamera(640, 480, 973.3079, 973.3079, 320, 240)
    vo = VisualOdometry(cam)
    
    while True:
        if synced_data:
            frame, x_imu, y_imu, theta_imu = synced_data.popleft()
            scale = cal_distance(last_x_imu, last_y_imu, x_imu, y_imu)
            scale = 0.02
            vo.update(frame, scale)
            if vo.cur_t is not None:
                with open(vo_dir, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([vo.cur_t[0], vo.cur_t[1], vo.cur_t[2]])
                vio_x = float((alpha)*x_imu + (1-alpha)*vo.cur_t[2]) 
                vio_y = float((alpha)*y_imu - (1-alpha)*vo.cur_t[0]) 
                with open(vio_dir, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([vio_x, vio_y])
            last_x_imu = x_imu
            last_y_imu = y_imu

def camera_thread():
    cam = RPiCamera(640, 480, 973.3079, 973.3079, 320, 240)
    cam.PiCamera_Init()
    cam.start_camera()
    count = 0
    # with open('imu.csv', 'w', newline='') as file:
    #     file.write("")
    os.mkdir(img_dir)
    while True:
        timestamp, frame = cam.capture_img()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        if imu_queue:
            imu_data = imu_queue.popleft() 
            ts_imu, data = imu_data

            # Ghi vào file log
            x_imu, y_imu, theta_imu = imu_calculate(data, imu_dir)
            # log_file.write(f"{timestamp:.6f} {count:06d} {ts_imu:.6f} \n")
            frameName = f"{count:06d}.png"
            cv2.imwrite(f"{img_dir}/{frameName}", gray)
            synced_data.append((gray, x_imu, y_imu, theta_imu))
            count = count + 1
        else:
            imu_text = "IMU: no data"

if __name__ == "__main__":
    # Tạo các tiến trình
    process1 = Thread(target=ble_thread, daemon=True)
    process2 = Thread(target=car_ctrl_thread, daemon=True)
    process3 = Thread(target=camera_thread, daemon=True)
    process4 = Thread(target=vio_thread, daemon=True)

    # Khởi động các tiến trình
    process1.start()
    process2.start()
    process3.start()
    process4.start()

    # Đợi cả hai tiến trình hoàn thành
    process1.join()
    process2.join()
    process3.join()
    process4.join()

    print("Done!")