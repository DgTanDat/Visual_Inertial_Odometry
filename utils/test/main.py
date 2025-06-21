import threading
import time
from datetime import datetime
import math
import csv
from camera import *
from database import *
from global_interface import *
from imu import *
from motorControl import *

data = [
    ['timeStamp', 'curFaccX', 'curFaccY', 'curFaccZ', 'curRoll', 'curPitch', 'curYaw', 'curWX', 'curWY', 'curWZ', 'positionX', 'positionY', 'curVelX', 'curVelY', 'focusYaw'],
]

directory = "/home/dat/record/imu"
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{current_datetime}.csv"
fileVideopath = f"/home/dat/record/camera/{current_datetime}.mp4"

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

def processNotifyTask():
    STABLE_THREADHOLD = 4
    global NONE
    global STOP 
    global TURNLEFT
    global GOSTRAIGHT 
    global TURNRIGHT
    global delta_t
    global count, IS_RUNNING

    high_threadhold = 0.05
    low_threadhold = -0.05

    statePN = NONE
    lastStatePN = NONE

    initLastState = GOSTRAIGHT
    initState = GOSTRAIGHT

    haveInitYaw = False
    angle_thread_high = 0
    angle_thread_low = 0

    waitTime = 0

    focusYaw = 0
    curYaw = 0
    lastYaw = 0

    positionX = 0
    positionY = 0

    startPosX = 0
    startPosY = 0

    curFaccX = 0
    curFaccY = 0

    lastFaccX = 0
    lastFaccY = 0

    counterX = 0
    counterY = 0

    curVelX = 0
    curVelY = 0

    lastVelX = 0
    lastVelY = 0

    timeStamp   = 0   
    curRoll     = 0
    curPitch    = 0
    curYaw      = 0
    curFaccX    = 0
    curFaccY    = 0
    curFaccZ    = 0
    curWX       = 0
    curWY       = 0
    curWZ       = 0

    while True:
        if (not notifyQueue.empty()) and (not lastStateQueue.empty()):
            notifyDatas = notifyQueue.get()
            lastStatePN = lastStateQueue.get()
            timeStamp   = convertData(notifyDatas, 0)
            curRoll     = convertData(notifyDatas, 4)
            curPitch    = convertData(notifyDatas, 8)
            curYaw      = convertData(notifyDatas, 12)
            curFaccX    = convertData(notifyDatas, 16) 
            curFaccY    = convertData(notifyDatas, 20)
            curFaccZ    = convertData(notifyDatas, 24)
            curWX       = convertData(notifyDatas, 28)
            curWY       = convertData(notifyDatas, 32)
            curWZ       = convertData(notifyDatas, 36)

            if not haveInitYaw:
                focusYaw = curYaw
                haveInitYaw = True

            
            if lastStatePN == STOP:  
                waitTime -= 1
                if waitTime <= 0:  
                    if not nextStateQueue.empty():
                        statePN = nextStateQueue.get()
                        leftAngle_thread_high = cal_angle(curYaw, 80)
                        leftAngle_thread_low = cal_angle(curYaw, 75)
                        rightAngle_thread_high = cal_angle(curYaw, -75)
                        rightAngle_thread_low = cal_angle(curYaw, -80)
                    else:
                        statePN = STOP
                        IS_RUNNING = False
                else:
                    statePN = STOP
            elif lastStatePN == GOSTRAIGHT:
                
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
                if counterY>= STABLE_THREADHOLD:
                    curVelY = 0

                curVelX += (curFaccX)*delta_t
                curVelY += (curFaccY)*delta_t

                positionX += (curVelX)*delta_t
                positionY += (curVelY)*delta_t
                distance = cal_distance(startPosX, startPosY, positionX, positionY)
                # print("distance: %f", distance)
                if distance >= 0.96:
                    statePN = STOP
                    startPosX = positionX
                    startPosY = positionY
                else:
                    statePN = GOSTRAIGHT   
            elif lastStatePN == TURNLEFT:
                if curYaw >= leftAngle_thread_low and curYaw <= leftAngle_thread_high:
                    waitTime = 10
                    statePN = STOP
                else:
                    statePN = TURNLEFT
            elif lastStatePN == TURNRIGHT:
                if curYaw >= rightAngle_thread_low and curYaw <= rightAngle_thread_high:
                    waitTime = 10
                    statePN = STOP
                else:
                    statePN = TURNRIGHT
            else:
                statePN = STOP
         
            print(curYaw)
            print(curFaccX)
            print(curFaccY)
            write_to_csv(f"{directory}/{filename}", timeStamp, curFaccX, curFaccY, curFaccZ, curRoll, curPitch, curYaw, curWX, curWY, curWZ, positionX, positionY, curVelX, curVelY, focusYaw)
            stateQueue.put(statePN)
    
            lastYaw = curYaw
            lastFaccX = curFaccX
            lastFaccY = curFaccY
            lastVelX = curVelX
            lastVelY = curVelY    
        time.sleep(1e-6)

def processStateTask():
    global NONE
    global STOP 
    global TURNLEFT
    global GOSTRAIGHT 
    global TURNRIGHT
    stateSP = NONE
    lastStateSP = NONE
    while True:
        if not stateQueue.empty():
            stateSP = stateQueue.get()
            if lastStateSP != stateSP:
                if stateSP == STOP:
                    brake()
                    
                elif stateSP == GOSTRAIGHT:
                    forward(40)
                    
                elif stateSP == TURNLEFT:
                    turnLeft(55)
                    
                elif stateSP == TURNRIGHT:
                    turnRight(55)
                else:
                    stateSP = STOP
                    brake()
             
                lastStateSP = stateSP
            lastStateQueue.put(lastStateSP)
        time.sleep(1e-6)

if __name__ == "__main__":
    get_inst() 

    with open(f"{directory}/{filename}", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    imu = IMUManager(IMU_FREQ)
    imu.imu_init()
    cam = RPiCamera(640, 480, 970, 961, 320, 240)
    cam.PiCamera_Init()

    # Keep the program running to listen for notifications
    try:
        pstateTask = threading.Thread(target=processStateTask)
        pnotifyTask = threading.Thread(target=processNotifyTask)
        # picamera_start_record(fileVideopath)
        pstateTask.start()
        pnotifyTask.start()

        while True:
            if not IS_RUNNING:
                brake()
                # picamera_stop_record()
                imu.disconnect()
                print("Disconnected.")
                break
            time.sleep(1e-6)
        
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
