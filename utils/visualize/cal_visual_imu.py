# importing csv module

import matplotlib.pyplot as plt
import csv
# import statsmodels.api as sm
import pandas as pd
import numpy as np

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# csv file name
filename = "/home/dat/record/raw_imu/2025-06-21_12-29-11.csv" #"/home/dat/record/raw_imu/2025-06-21_12-25-11.csv"
#"rpgoa.csv"#"D0608a.csv"

import numpy as np

def rotate_to_north(x_local, y_local, yaw_deg):
    x_local = np.array(x_local)
    y_local = np.array(y_local)
    yaw_rad = np.deg2rad(yaw_deg)
    x_north =  x_local * np.cos(yaw_rad) + y_local * np.sin(yaw_rad)
    y_north = - x_local * np.sin(yaw_rad) + y_local * np.cos(yaw_rad)

    return x_north, y_north


f = 30
delta_t = 1/f
threadhold = 0.2

initYAW = 0
packCounter = [] 
timeStamp = []
eulerX = [] 
eulerY = []
eulerZ = [] 
faccX = []
faccY = [] 
faccZ = []

accX = []
accY = [] 
accZ = []

velX = []
velY = []
velZ = []

cur_accX = 0
cur_accY = 0
cur_accZ = 0

cur_velX = 0
cur_velY = 0
cur_velZ = 0

posX = []
posY = []
xlocal = []
ylocal = []

isturn = []

cur_posX = 0
cur_posY = 0
cur_posZ = 0

start_posX = 0
start_posY = 0
start_posZ = 0

counter = 0
step = 0
counterX = 0
counterY = 0
counterZ = 0
sample = 8
counter_turn = 0
counter_forward = 0
# i = []
timer_wait_stable = 0

def cal_distance(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))**(0.5)
Init = False
# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)

    for row in csvreader: 
       
        eulerZ.append(float(row[2]))
        faccX.append(float(row[0]))
        faccY.append(float(row[1]))
        packCounter.append(counter)
        if not Init:
            initYAW = float(row[2])
            Init = True
        counter = counter+1

      
        if abs(float(row[0])) <= threadhold:
            cur_accX = 0
            counterX += 1
        else:
            cur_accX = float(row[0])
            counterX = 0           

        if abs(float(row[1])) <= threadhold:
            cur_accY = 0
            counterY += 1
        else:
            cur_accY = float(row[1])
            counterY = 0           

            # if abs(float(row[7])-0.33) <= threadhold:
            #     cur_accZ = 0
            #     counterZ += 1
            # else: 
            #     cur_accZ = (float(row[7])-0.33)
            #     counterZ = 0

        if counterX >= sample:
            cur_velX = 0
        else:
            cur_velX += (cur_accX)*delta_t
            
        if counterY >= sample:
            cur_velY = 0
        else:
            cur_velY += (cur_accY)*delta_t

            # if counterZ >= sample:
            #     cur_velZ = 0
            # else:
            #     cur_velZ += (cur_accZ)*delta_t

        if int(eulerZ[counter-2]) != int(eulerZ[counter-1]):
            counter_turn += 1
            counter_forward = 0
        else:
            counter_forward += 1
            if counter_forward >= 10:
                counter_turn = 0
                    
        if(counter_turn >= 10):
            timer_wait_stable = 15#15
            isturn.append(1)
        else:
            isturn.append(-1)

        if timer_wait_stable > 0:          
            cur_accX = 0
            cur_accY = 0

            cur_velX = 0
            cur_velY = 0
              
            timer_wait_stable -= 1

        cur_posX += (cur_velX)*delta_t
        cur_posY += (cur_velY)*delta_t
        
            # cur_posZ += (cur_velZ)*delta_t 

        # xlocal.append(x)
        # ylocal.append(y)
        accX.append(cur_accX)
        accY.append(cur_accY)
            # accZ.append(cur_accZ)

        velX.append(cur_velX)
        velY.append(cur_velY)
            # velZ.append(cur_velZ)

            # cur_velX += cur_accX*delta_t
            # cur_velY += cur_accY*delta_t
            # cur_velZ += cur_accZ*delta_t

            # cur_posX += cur_velX*delta_t
            # cur_posY += cur_velY*delta_t
            # cur_posZ += cur_velZ*delta_t   
        posX.append(cur_posX)
        posY.append(cur_posY)
            # posZ.append(cur_posZ)
    

xlocal, ylocal = rotate_to_north(posX, posY, initYAW)
faccXStd = []
##### standardize the data #####
meanAccX = np.mean(eulerZ)
stdAccX = np.std(eulerZ)
Q1 = np.percentile(eulerZ, 25)
Q3 = np.percentile(eulerZ, 75)
IQR = Q3 - Q1
for i in eulerZ:
    faccXStd.append((i - meanAccX)/stdAccX)
 
fft_values = np.fft.fft(faccX)
fft_freqs = np.fft.fftfreq(len(faccX), 1/f)

positive_freqs = fft_freqs[fft_freqs >= 0]
positive_fft = np.abs(fft_values[fft_freqs >= 0])

plt.plot(packCounter, faccX, color = 'g',  
         marker = 'o', label='facc x')
plt.xticks([0, 200, 400, 600, 800])
plt.axhline(y=0.2, color='r', linestyle='--', linewidth=1, label='y = 0.2')
plt.axhline(y=-0.2, color='b', linestyle='--', linewidth=1, label='y = -0.2')
plt.axvline(x=180, color='purple', linestyle='--', linewidth=1, label='x = 180')
plt.grid() 
plt.legend()
plt.tight_layout()
plt.show()



figure, axis = plt.subplots(2, 2)


axis[0, 0].plot(packCounter, faccX, color = 'g',  
         marker = 'o', label='facc x')

axis[0, 0].plot(packCounter, velX, color = 'r',  
         marker = 'o', label='vel')
axis[0, 0].plot(packCounter, posX, color = 'b',  
         marker = 'o', label='pos')
# axis[0, 0].set_title("facc x")
axis[0, 0].grid() 
axis[0, 0].legend()


axis[0, 1].plot(packCounter, faccY, color = 'g',  
         marker = 'o', label='facc y')
axis[0, 1].plot(packCounter, velY, color = 'r',  
         marker = 'o', label='vel y')
axis[0, 1].plot(packCounter, posY, color = 'b',  
         marker = 'o', label='pos y')

axis[0, 1].grid() 
axis[0, 1].legend()


axis[1, 0].plot(packCounter, eulerZ, color = 'g',  
         marker = 'o', label='euler z')

axis[1, 0].grid() 
axis[1, 0].legend()


axis[1, 1].plot(posX, posY, color = 'g',  
         marker = 'o', label='x')
axis[1, 1].plot(xlocal, ylocal, color = 'r',  
         marker = 'o', label='x')

axis[1, 1].grid() 
axis[1, 1].legend()
 
axis[0, 0].set_xticks([0, 200, 400, 600, 800])
axis[0, 1].set_xticks([0, 200, 400, 600, 800])
axis[1, 0].set_xticks([0, 200, 400, 600, 800])

plt.show() 

 