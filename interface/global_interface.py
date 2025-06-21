from queue import Queue
from collections import deque


SYS_CNT = 0
STOP = 1
GOSTRAIGHT = 0
TURNLEFT = 2
TURNRIGHT = 3
NONE = -1
IS_RUNNING = True
IMU_FREQ = 30
delta_t = 1/IMU_FREQ 
# packageCounter = 3*IMU_FREQ 
# count = 0

high_threadhold = 0.2
low_threadhold = -0.2
STABLE_THREADHOLD = 5

counterX = 0
counterY = 0
curVelX = 0
curVelY = 0
positionX = 0
positionY = 0
init_Yaw = None
last_Yaw = 0
counter_turn = 0
counter_forward = 0
timer_wait_stable = 0
scale = 0.02

notifyQueue = Queue(maxsize = 30)
stateQueue = Queue(maxsize = 30)
lastStateQueue = Queue(maxsize = 30)
nextStateQueue = Queue(maxsize = 180)

image_queue = deque(maxlen=2)
imu_queue = deque(maxlen=10)
synced_data = deque(maxlen=180)