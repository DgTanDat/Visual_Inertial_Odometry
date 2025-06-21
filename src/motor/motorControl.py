from src.motor.motorDriver import *

m = MotorDriver()

bias = 10

def turnLeft(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(2, BACKWARD, speed + bias)
    m.motor(3, FORWARD, speed + bias)
    m.motor(4, FORWARD, speed)
    m.run()

def turnRight(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed + bias)
    m.motor(3, BACKWARD, speed + bias)
    m.motor(4, BACKWARD, speed)
    m.run()

def forward(speed):
    m.motor(1, FORWARD, speed)
    m.motor(2, FORWARD, speed)
    m.motor(3, FORWARD, speed)
    m.motor(4, FORWARD, speed)
    m.run()

def backward(speed):
    m.motor(1, BACKWARD, speed)
    m.motor(4, BACKWARD, speed)
    m.motor(3, BACKWARD, speed)
    m.motor(2, BACKWARD, speed)
    m.run()

def brake(): 
    m.motor(1, BRAKE, 0)
    m.motor(2, BRAKE, 0)
    m.motor(3, BRAKE, 0)
    m.motor(4, BRAKE, 0)
    m.run()

def release():
    m.motor(1, RELEASE, 0)
    m.motor(2, RELEASE, 0)
    m.motor(3, RELEASE, 0)
    m.motor(4, RELEASE, 0)
    m.run()



