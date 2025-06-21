from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import threading

# Define motor bit control
MOTOR1_A = 2
MOTOR1_B = 3
MOTOR2_A = 1
MOTOR2_B = 4
MOTOR3_A = 5
MOTOR3_B = 7
MOTOR4_A = 0
MOTOR4_B = 6

# PWM pins
MOTOR1_PWM = 14
MOTOR2_PWM = 13
MOTOR3_PWM = 12
MOTOR4_PWM = 15

# Shift register pins
MOTORLATCH = 17
MOTORENABLE = 24
MOTORDATA = 25
MOTORCLK = 5

FORWARD = 1
BACKWARD = 2
BRAKE = 3
RELEASE = 4

HIGH = 1
LOW = 0

# factory = PiGPIOFactory()

# Function to handle motor control
class MotorDriver:
    def __init__(self):
        self.pwm = None    

        self.motor1_pwm = PWMOutputDevice(MOTOR1_PWM)
        self.motor2_pwm = PWMOutputDevice(MOTOR2_PWM)
        self.motor3_pwm = PWMOutputDevice(MOTOR3_PWM)
        self.motor4_pwm = PWMOutputDevice(MOTOR4_PWM)

        # self.motor1_pwm = PWMOutputDevice(MOTOR1_PWM, pin_factory=factory)
        # self.motor2_pwm = PWMOutputDevice(MOTOR2_PWM, pin_factory=factory)
        # self.motor3_pwm = PWMOutputDevice(MOTOR3_PWM, pin_factory=factory)
        # self.motor4_pwm = PWMOutputDevice(MOTOR4_PWM, pin_factory=factory)

        self.motor1_pwm.frequency = 1000
        self.motor2_pwm.frequency = 1000
        self.motor3_pwm.frequency = 1000
        self.motor4_pwm.frequency = 1000
        
        # Initialize shift register pins (if applicable, modify as needed)
        self.motor_latch = DigitalOutputDevice(MOTORLATCH)
        self.motor_enable = DigitalOutputDevice(MOTORENABLE)
        self.motor_data = DigitalOutputDevice(MOTORDATA)
        self.motor_clk = DigitalOutputDevice(MOTORCLK)
        
        self.shift_register_initialized = False
        self.latch_copy = 0

    def motor(self, nMotor, command, speed):
        motorA, motorB = None, None

        if 1 <= nMotor <= 4:
            if nMotor == 1:
                motorA, motorB = MOTOR1_A, MOTOR1_B
                self.pwm = self.motor1_pwm
            elif nMotor == 2:
                motorA, motorB = MOTOR2_A, MOTOR2_B
                self.pwm = self.motor2_pwm
            elif nMotor == 3:
                motorA, motorB = MOTOR3_A, MOTOR3_B
                self.pwm = self.motor3_pwm
            elif nMotor == 4:
                motorA, motorB = MOTOR4_A, MOTOR4_B
                self.pwm = self.motor4_pwm

            if command == FORWARD:
                self.motor_output(motorA, HIGH, speed)
                self.motor_output(motorB, LOW, speed)
            elif command == BACKWARD:
                self.motor_output(motorA, LOW, speed)
                self.motor_output(motorB, HIGH, speed)
            elif command == BRAKE:
                self.motor_output(motorA, LOW, 0)
                self.motor_output(motorB, LOW, 0)
            elif command == RELEASE:
                self.motor_output(motorA, LOW, 0)
                self.motor_output(motorB, LOW, 0)
    
    def motor_output(self, output, high_low, speed):
        self.shift_write(output, high_low)
        if speed == -1:  # No PWM set
            self.pwm.off()
        if speed in range(0, 101):
            self.pwm.value = speed / 100.0  # Convert to a 0-1 scale for PWM
    
    def shift_write(self, output, high_low):
        if not self.shift_register_initialized:
            self.motor_data.off()
            self.motor_latch.off()
            self.motor_clk.off()
            self.motor_enable.off()

            self.shift_register_initialized = True

        self.bit_write(output, high_low)
        
        # self.shift_out()
        # time.sleep(1e-7)
        # self.motor_latch.on()
        # time.sleep(1e-7)
        # self.motor_latch.off()
        # Implement shift register control (if needed)
        # For simplicity, you can control GPIO pins directly for motor control
        
    def bit_write(self, bitIndex, signal):
        if signal == 1:
            self.latch_copy |=  (1 << bitIndex)
        else:
            self.latch_copy &= ~(1 << bitIndex)

    def shift_out(self):
        binValue = self.latch_copy
        self.motor_clk.off()
        for i in range(0,8):
            if (binValue >> (8 - 1 - i) & 1) == 1:
                self.motor_data.on()
            else:
                self.motor_data.off()
            self.motor_clk.on()
            time.sleep(1e-7)
            self.motor_clk.off()
            time.sleep(1e-7)

    def run(self):
        self.shift_out()
        self.motor_latch.on()
        self.motor_latch.off()


