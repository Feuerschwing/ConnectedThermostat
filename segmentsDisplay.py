import time
from pyA20.gpio import gpio
from pyA20.gpio import port
import array
import threading

verrou = threading.RLock()

class Display:
    #broches: - 0 :
    def __init__(self, data_pin, latch_pin, clock_pin, d1_pin, d2_pin, d3_pin, d4_pin):
        self.deg = 0x97
        self.LED0 = [0b01111101,0x44,0b1011011,0b01011110,0b1100110,0b00111110,0b00111111,0b01010100,0b01111111,0b01111110]	#original mode
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.d1_pin = d1_pin
        self.d2_pin = d2_pin
        self.d3_pin = d3_pin
        self.d4_pin = d4_pin
        self.i = 0
        gpio.setcfg(data_pin, gpio.OUTPUT)
        gpio.setcfg(latch_pin, gpio.OUTPUT)
        gpio.setcfg(clock_pin, gpio.OUTPUT)
        gpio.setcfg(d1_pin, gpio.OUTPUT)
        gpio.setcfg(d2_pin, gpio.OUTPUT)
        gpio.setcfg(d3_pin, gpio.OUTPUT)
        gpio.setcfg(d4_pin, gpio.OUTPUT)
        self.outputs = [gpio.LOW] * 8
        self.lock = 0

    def display(self, displayValue):
        if(self.lock == 0):
            self.lock = 1
            self.reset()
            if(self.i == 0):
                self.i +=1
                self.latch(self.LED0[(displayValue/10)%10], 1)
            elif(self.i == 1):
                self.i +=1
                self.latch(self.LED0[displayValue%10], 2)
            elif(self.i == 2):
                self.i +=1
                self.latch(0b1110010, 3)
            elif(self.i == 3):
                self.i = 0
                self.latch(0b0111001, 4)
            self.lock = 0

    def reset(self):
        gpio.output(self.d1_pin, gpio.HIGH)
        gpio.output(self.d2_pin, gpio.HIGH)
        gpio.output(self.d3_pin, gpio.HIGH)
        gpio.output(self.d4_pin, gpio.HIGH)

    def setOutput(self, output_number, value):
        try:
            self.outputs[output_number] = value
        except IndexError:
            raise ValueError("Invalid output number. Can be only an int from 0 to 7")

    def setOutputs(self, outputs):
        if 8 != len(outputs):
            raise ValueError("setOutputs must be an array with 8 elements")

        self.outputs = outputs

    def latch(self, hex, digit):
        gpio.output(self.latch_pin, gpio.LOW)
        for i in range(7, -1, -1):
            gpio.output(self.clock_pin, gpio.LOW)
            gpio.output(self.data_pin, (hex>>7-i)&0x01)
            gpio.output(self.clock_pin, gpio.HIGH)
        gpio.output(self.latch_pin, gpio.HIGH)
        if(digit == 1):
            gpio.output(self.d1_pin, gpio.LOW)
        if(digit == 2):
            gpio.output(self.d2_pin, gpio.LOW)
        if(digit == 3):
            gpio.output(self.d3_pin, gpio.LOW)
        if(digit == 4):
            gpio.output(self.d4_pin, gpio.LOW)
