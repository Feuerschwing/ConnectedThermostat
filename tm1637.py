from pyA20.gpio import gpio
from pyA20.gpio import port
import time


HEXDIGITS = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f]

HEXLETTERS = {
    'A': 0x77,
    'B': 0x7f,
    'b': 0x7C,
    'C': 0x39,
    'c': 0x58,
    'D': 0x3f,
    'd': 0x5E,
    'E': 0x79,
    'F': 0x71,
    'G': 0x7d,
    'H': 0x76,
    'h': 0x74,
    'I': 0x06,
    'J': 0x1f,
    'K': 0x76,
    'L': 0x38,
    'l': 0x06,
    'n': 0x54,
    'O': 0x3f,
    'o': 0x63,
    'P': 0x73,
    'r': 0x50,
    'S': 0x6d,
    'U': 0x3e,
    'V': 0x3e,
    'Y': 0x66,
    'Z': 0x5b,
    ' ': 0x00,
    'T1': 0x07,
    'T2': 0x31,
    'M1': 0x33,
    'M2': 0x27,
    'W1': 0x3c,
    'W2': 0x1e
}

ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0
BRIGHT_DARKEST = 0
BRIGHT_DEFAULT = 2
BRIGHT_HIGHEST = 7


class TM1637:
    __doublepoint = False
    __clk_pin = 0
    __data_pin = 0
    __brightness = BRIGHT_DEFAULT
    __current_data = [' ', ' ', ' ', ' ']

    def __init__(self, clock_pin, data_pin, brightness=BRIGHT_DEFAULT):
        self.__clk_pin = clock_pin
        self.__data_pin = data_pin
        self.__brightness = brightness
        gpio.setcfg(self.__clk_pin, gpio.OUTPUT)
        gpio.setcfg(self.__data_pin, gpio.OUTPUT)

    def clear(self):
        b = self.__brightness
        point = self.__doublepoint
        self.__brightness = 0
        self.__doublepoint = False
        data = [' ', ' ', ' ', ' ']
        self.set_values(data)
        self.__brightness = b
        self.__doublepoint = point

    def set_values(self, data):
        for i in range(4):
            self.__current_data[i] = data[i]

        self.start()
        self.write_byte(ADDR_AUTO)
        self.stop()
        self.start()
        self.write_byte(STARTADDR)
        for i in range(4):
            self.write_byte(self.encode(data[i]))
        self.stop()
        self.start()
        self.write_byte(0x88 + self.__brightness)
        self.stop()

    def set_value(self, value, index):
        if index not in range(4):
            pass

        self.__current_data[index] = value;

        self.start()
        self.write_byte(ADDR_FIXED)
        self.stop()
        self.start()
        self.write_byte(STARTADDR | index)
        self.write_byte(self.encode(value))
        self.stop()
        self.start()
        self.write_byte(0x88 + self.__brightness)
        self.stop()

    def set_brightness(self, brightness):
        if brightness not in range(8):
            pass

        self.__brightness = brightness
        self.set_values(self.__current_data)

    def set_doublepoint(self, value):
        self.__doublepoint = value
        self.set_values(self.__current_data)

    def encode(self, data):
        point = 0x80 if self.__doublepoint else 0x00;

        if data == 0x7F:
            data = 0
        elif HEXLETTERS.has_key(data):
            data = HEXLETTERS[data] + point
        else:
            data = HEXDIGITS[data] + point
        return data

    def write_byte(self, data):
        for i in range(8):
            gpio.output(self.__clk_pin, gpio.LOW)
            if data & 0x01:
                gpio.output(self.__data_pin, gpio.HIGH)
            else:
                gpio.output(self.__data_pin, gpio.LOW)
            data >>= 1
            gpio.output(self.__clk_pin, gpio.HIGH)

        gpio.output(self.__clk_pin, gpio.LOW)
        gpio.output(self.__data_pin, gpio.HIGH)
        gpio.output(self.__clk_pin, gpio.HIGH)
        gpio.setcfg(self.__data_pin, gpio.INPUT)

        while gpio.input(self.__data_pin):
            time.sleep(0.001)
            if gpio.input(self.__data_pin):
                gpio.setcfg(self.__data_pin, gpio.OUTPUT)
                gpio.output(self.__data_pin, gpio.LOW)
                gpio.setcfg(self.__data_pin, gpio.INPUT)
        gpio.setcfg(self.__data_pin,  gpio.OUTPUT)

    def start(self):
        gpio.output(self.__clk_pin, gpio.HIGH)
        gpio.output(self.__data_pin, gpio.HIGH)
        gpio.output(self.__data_pin, gpio.LOW)
        gpio.output(self.__clk_pin, gpio.LOW)

    def stop(self):
        gpio.output(self.__clk_pin, gpio.LOW)
        gpio.output(self.__data_pin, gpio.LOW)
        gpio.output(self.__clk_pin, gpio.HIGH)
        gpio.output(self.__data_pin, gpio.HIGH)

    def cleanup(self):
        gpio.cleanup(self.__clk_pin)
        gpio.cleanup(self.__data_pin)
