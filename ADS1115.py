from smbus2 import SMBus
import time
from math import log

ADS1015_ADDRESS = 0x48
#POINTER REGISTER

ADS1015_REG_POINTER_MASK = 0x03      # Point mask
ADS1015_REG_POINTER_CONVERT  = 0x00   # Conversion
ADS1015_REG_POINTER_CONFIG = 0x01    # Configuration
ADS1015_REG_POINTER_LOWTHRESH  = 0x02 # Low threshold
ADS1015_REG_POINTER_HITHRESH = 0x03  # High threshold

#=========================================================================
#CONFIG REGISTER

ADS1015_REG_CONFIG_OS_MASK  = 0x8000 # OS Mask
ADS1015_REG_CONFIG_OS_SINGLE = 0x8000 # Write: Set to start a single-conversion
ADS1015_REG_CONFIG_OS_BUSY = 0x0000 # ///< Read: Bit = 0 when conversion is in progress
ADS1015_REG_CONFIG_OS_NOTBUSY = 0x8000 # ///< Read: Bit = 1 when device is not performing a conversion

ADS1015_REG_CONFIG_MUX_MASK = 0x7000 #< Mux Mask

ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000 # ///< Single-ended AIN0
ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000 #///< Single-ended AIN1
ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000 #///< Single-ended AIN2
ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000 #///< Single-ended AIN3

ADS1015_REG_CONFIG_PGA_MASK = 0x0E00   #///< PGA Mask
ADS1015_REG_CONFIG_PGA_6_144V  = 0x0000 #///< +/-6.144V range = Gain 2/3
ADS1015_REG_CONFIG_PGA_4_096V = 0x0200 #///< +/-4.096V range = Gain 1
ADS1015_REG_CONFIG_PGA_2_048V = 0x0400 #///< +/-2.048V range = Gain 2 (default)
ADS1015_REG_CONFIG_PGA_1_024V = 0x0600 #///< +/-1.024V range = Gain 4
ADS1015_REG_CONFIG_PGA_0_512V = 0x0800 #///< +/-0.512V range = Gain 8
ADS1015_REG_CONFIG_PGA_0_256V = 0x0A00 #///< +/-0.256V range = Gain 16

ADS1015_REG_CONFIG_MODE_MASK = 0x0100   #///< Mode Mask
ADS1015_REG_CONFIG_MODE_CONTIN = 0x0000 #///< Continuous conversion mode
ADS1015_REG_CONFIG_MODE_SINGLE = 0x0100 #///< Power-down single-shot mode (default)

ADS1015_REG_CONFIG_DR_MASK  = 0x00E0 #   ///< Data Rate Mask
ADS1015_REG_CONFIG_DR_128SPS = 0x0000 #///< 128 samples per second
ADS1015_REG_CONFIG_DR_250SPS = 0x0020 # ///< 250 samples per second
ADS1015_REG_CONFIG_DR_490SPS = 0x0040 # ///< 490 samples per second
ADS1015_REG_CONFIG_DR_920SPS = 0x0060 # ///< 920 samples per second
ADS1015_REG_CONFIG_DR_1600SPS = 0x0080 # ///< 1600 samples per second (default)
ADS1015_REG_CONFIG_DR_2400SPS = 0x00A0 #///< 2400 samples per second
ADS1015_REG_CONFIG_DR_3300SPS = 0x00C0 # ///< 3300 samples per second

ADS1015_REG_CONFIG_CMODE_MASK = 0x0010 #///< CMode Mask
ADS1015_REG_CONFIG_CMODE_TRAD = 0x0000 #///< Traditional comparator with hysteresis (default)
ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010 #///< Window comparator

ADS1015_REG_CONFIG_CPOL_MASK = 0x0008 #///< CPol Mask
ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000 # ///< ALERT/RDY pin is low when active (default)
ADS1015_REG_CONFIG_CPOL_ACTVHI = 0x0008 # ///< ALERT/RDY pin is high when active

ADS1015_REG_CONFIG_CLAT_MASK = 0x0004 #///< Determines if ALERT/RDY pin latches once asserted
ADS1015_REG_CONFIG_CLAT_NONLAT = 0x0000 #///< Non-latching comparator (default)
ADS1015_REG_CONFIG_CLAT_LATCH = 0x0004 #///< Latching comparator

ADS1015_REG_CONFIG_CQUE_MASK = 0x0003 #///< CQue Mask
ADS1015_REG_CONFIG_CQUE_1CONV = 0x0000 #///< Assert ALERT/RDY after one conversions
ADS1015_REG_CONFIG_CQUE_2CONV = 0x0001 #///< Assert ALERT/RDY after two conversions
ADS1015_REG_CONFIG_CQUE_4CONV = 0x0002  #///< Assert ALERT/RDY after four conversions
ADS1015_REG_CONFIG_CQUE_NONE = 0x0003 #///< Disable the comparator and put ALERT/RDY in high state (default)

beta = 3950.0
Vcc = 3.3
R = 100000.0
r0 = 100000.0
t0 = 298.0

#Open i2c bus 1 and read one byte from address 80, offset 0
bus = SMBus(0)

print("adc instance")
def read_ADC(channel):
    conf_tab = []
    conf = ADS1015_REG_CONFIG_CQUE_NONE | ADS1015_REG_CONFIG_CLAT_NONLAT|ADS1015_REG_CONFIG_CPOL_ACTVLOW|ADS1015_REG_CONFIG_CMODE_TRAD|ADS1015_REG_CONFIG_DR_1600SPS|ADS1015_REG_CONFIG_MODE_SINGLE
    conf |= ADS1015_REG_CONFIG_OS_SINGLE
    if(channel == 0):
        conf |= ADS1015_REG_CONFIG_MUX_SINGLE_0
    if(channel == 1):
        conf |= ADS1015_REG_CONFIG_MUX_SINGLE_1
    if(channel == 2):
        conf |= ADS1015_REG_CONFIG_MUX_SINGLE_2
    if(channel == 3):
        conf |= ADS1015_REG_CONFIG_MUX_SINGLE_3

    conf_tab.append((conf>>8)&0xff)
    conf_tab.append(conf&0xff)

    bus.write_i2c_block_data(ADS1015_ADDRESS, ADS1015_REG_POINTER_CONFIG, conf_tab)
    time.sleep(0.1)
    return bus.read_i2c_block_data(ADS1015_ADDRESS, ADS1015_REG_POINTER_CONVERT, 2)

"""def main():
    byte_array = read_ADC(0)
    value = (byte_array[0]<<8)| byte_array[1]
    tension = (value * 0.1875)/1000.0
    rt = (tension/Vcc*R)/(1.0-tension/Vcc)
    temp = (log(rt/r0)/beta) + (1.0/t0)
    temp = 1.0/temp
    print("temperature adc 0 : ", temp - 273)

    byte_array = read_ADC(1)
    value = (byte_array[0]<<8)| byte_array[1]
    tension = (value * 0.1875)/1000.0
    rt = (tension/Vcc*R)/(1.0-tension/Vcc)
    temp = (log(rt/r0)/beta) + (1.0/t0)
    temp = 1.0/temp
    print("temperature adc 1 : ", temp - 273)"""


"""if __name__ == "__main__":
    while(1):
        main()
        time.sleep(2)"""
