from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep, time
import logging
from threading import Timer
from os import getenv
import singletonHistorian



logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(getenv('DEBUG') or logging.INFO)


class Encoder:

    clk = None
    dt = None
    sw = None

    polling_interval = 5  # Polling interval (in ms)
    sw_debounce_time = 250  # Debounce time (for switch only)

    step = 1  # Scale step from min to max
    max_counter = 25  # Scale max
    min_counter = 15  # Scale min
    counter = 0  # Initial scale position
    counter_loop = False  # If True, when at MAX, loop to MIN (-> 0, ..., MAX, MIN, ..., ->)

    clkLastState = None

    inc_callback = None  # Clockwise rotation (increment)
    dec_callback = None  # Anti-clockwise rotation (decrement)
    chg_callback = None  # Rotation (either way)
    sw_callback = None  # Switch pressed

    def __init__(self, CLK=None, DT=None, SW=None, polling_interval=1):
        self.clk = CLK
        self.dt = DT
        gpio.init()
        #GPIO.setmode(GPIO.BCM)
        gpio.setcfg(self.clk, gpio.INPUT)
        gpio.pullup(self.clk, gpio.PULLDOWN)
        gpio.setcfg(self.dt, gpio.INPUT)
        gpio.pullup(self.dt, gpio.PULLDOWN)

        if SW is not None:
            self.sw = SW
            gpio.setcfg(self.sw, gpio.INPUT)
            gpio.pullup(self.sw, gpio.PULLUP)
        self.clkLastState = gpio.input(self.clk)
        self.polling_interval = polling_interval

    def setup(self, **params):

        # Note: boundaries are inclusive : [min_c, max_c]

        if 'loop' in params and params['loop'] is True:
            self.counter_loop = True
        else:
            self.counter_loop = False

        self.counter = self.min_counter + 0
        if 'scale_min' in params:
            self.min_counter = params['scale_min']
        if 'scale_max' in params:
            self.max_counter = params['scale_max']
        if 'step' in params:
            self.step = params['step']
        if 'inc_callback' in params:
            self.inc_callback = params['inc_callback']
        if 'dec_callback' in params:
            self.dec_callback = params['dec_callback']
        if 'chg_callback' in params:
            self.chg_callback = params['chg_callback']
        if 'sw_callback' in params:
            self.sw_callback = params['sw_callback']
        if 'sw_debounce_time' in params:
            self.sw_debounce_time = params['sw_debounce_time']
        if 'initial_counter' in params:
            self.counter = params['initial_counter']

    def set_counter(self, counter):
        self.counter = counter

    def watch(self):

        swTriggered = False  # Used to debounce a long switch click (prevent multiple callback calls)
        latest_switch_call = None
        while True:
            try:
                # Switch part
                if self.sw_callback:
                    if gpio.input(self.sw) == gpio.LOW:
                        if not swTriggered:
                            now = time() * 1000
                            if latest_switch_call:
                                if now - latest_switch_call > self.sw_debounce_time:
                                    self.sw_callback()
                            else:  # First call
                                self.sw_callback()
                        swTriggered = True
                        latest_switch_call = now
                    else:
                        swTriggered = False

                # Encoder part
                clkState = gpio.input(self.clk)
                dtState = gpio.input(self.dt)

                if clkState != self.clkLastState:

                    if dtState != clkState:
                        if self.counter + self.step <= self.max_counter:
                            # Loop or not, increment if the max isn't reached
                            self.counter += self.step
                        elif (self.counter + self.step >= self.max_counter) and self.counter_loop is True:
                            # If loop, go back to min once max is reached
                            self.counter = self.min_counter
                        if self.inc_callback is not None:
                            self.inc_callback(self.counter)
                        if self.chg_callback is not None:
                            self.chg_callback(self.counter)
                    else:
                        if self.counter - self.step >= self.min_counter:
                            # Same as for max ^
                            self.counter -= self.step
                        elif (self.counter - self.step <= self.min_counter) and self.counter_loop is True:
                            # If loop, go back to max once min is reached
                            self.counter = self.max_counter

                        if self.dec_callback is not None:
                            self.dec_callback(self.counter)
                        if self.chg_callback is not None:
                            self.chg_callback(self.counter)

                self.clkLastState = clkState
                sleep(self.polling_interval / 1000)
            except BaseException as e:
                logger.info("Exiting...")
                logger.info(e+" hehe")
                #GPIO.cleanup()
                break
