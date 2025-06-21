import threading
from multiprocessing import Process, Event
import time
from datetime import datetime
import math
import csv
from camera import *
from database import *
from global_interface import *
from imu import *
from car_ctrl import *
import cv2

data = [
    ['timeStamp', 'curFaccX', 'curFaccY', 'curFaccZ', 'curRoll', 'curPitch', 'curYaw', 'curWX', 'curWY', 'curWZ', 'positionX', 'positionY', 'curVelX', 'curVelY', 'focusYaw'],
]

directory = "/home/dat/record/imu"
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{current_datetime}.csv"
fileVideopath = f"/home/dat/record/camera/{current_datetime}.mp4"
img_dir = f"/home/dat/record/camera/{current_datetime}"
file = open(filename, mode='a', newline='')
writer = csv.writer(file)

def write_to_csv(filename, timeStamp, curFaccX, curFaccY, curFaccZ, curRoll, curPitch, curYaw, curWX, curWY, curWZ, positionX, positionY, curVelX, curVelY, focusYaw):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timeStamp, curFaccX, curFaccY, curFaccZ, curRoll, curPitch, curYaw, curWX, curWY, curWZ, positionX, positionY, curVelX, curVelY, focusYaw])

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

def ble_thread(stop_event, imu: IMUManager):
    imu.imu_init()

    try:
        while not stop_event.is_set():
            time.sleep(0.2)  
    finally:
        print("[BLE] stop thread. Disconnect...")
        imu.disconnect()


def car_ctrl_thread():
    controller = RobotController()
    controller.run()

def get_closest_imu(ts_frame):
    closest = None
    min_diff = float("inf")
    for ts_imu, imu_data in imu_queue:
        diff = abs(ts_imu - ts_frame)
        if diff < min_diff:
            min_diff = diff
            closest = (ts_imu, imu_data)
    return closest

if __name__ == "__main__":
    imu = IMUManager(60)
    cam = RPiCamera(640, 480, 970, 961, 320, 240)
        

    with open(f"{directory}/{filename}", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    # Keep the program running to listen for notifications
    try:
        # IMU_Task = threading.Thread(target=ble_thread)
        # CTRL_Task = threading.Thread(target=car_ctrl_thread)
        # IMU_Task.start()
        # CTRL_Task.start()

        stop_event = Event()
        IMU_Task = Process(target=ble_thread, args=(stop_event, imu,))
        CTRL_Task = Process(target=car_ctrl_thread)
        IMU_Task.start()
        CTRL_Task.start()
        
        cam.PiCamera_Init()
        cam.start_camera()

        prev_time = time.time()
        log_file = open("sync_log.txt", "w")
        count = 0
        while True:
            timestamp, frame = cam.capture_img()

            imu_data = get_closest_imu(timestamp)
            if imu_data:
                ts_imu, data = imu_data
                curYaw = convertData(data, 12)
                imu_text = f"IMU : {ts_imu:.3f}: {curYaw}"

                # Ghi vào file log
                log_file.write(f"{timestamp:.6f} {ts_imu:.6f} {data}\n")
                frameName = f"{count:06d}.png"
                cv2.imwrite(f"{img_dir}/{frameName}.jpg", frame)
                count = count + 1
            else:
                imu_text = "IMU: no data"

            # # FPS cal
            # now = time.time()
            # fps = 1.0 / (now - prev_time)
            # prev_time = now
            # fps_text = f"FPS: {fps:.2f}"
            # cv2.putText(frame, fps_text, (10, 60),
            #             fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            #             fontScale=0.6, color=(0, 255, 255), thickness=2)

            # Hiển thị overlay
            cv2.putText(frame, imu_text, (10, 30),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6, color=(0, 255, 0), thickness=2)


            cv2.imshow("Camera + IMU", frame)

            # Thoát bằng phím 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cam.stop_camera()
        log_file.close()
        brake()
        file.close()
        stop_event.set()
        cv2.destroyAllWindows()
    except KeyboardInterrupt:
        brake()
        file.close()
        print("Interrupted by user. Exiting.")
