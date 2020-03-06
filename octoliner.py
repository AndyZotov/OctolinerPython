# The MIT License (MIT)

import wiringpi as wp

OCTOLINER_DEFAULT_I2C_ADDRESS   = 0X2A
OCTOLINER_WHO_AM_I              = 0x00
OCTOLINER_RESET                 = 0x01
OCTOLINER_CHANGE_I2C_ADDR       = 0x02
OCTOLINER_SAVE_I2C_ADDR         = 0x03
OCTOLINER_PORT_MODE_INPUT       = 0x04
OCTOLINER_PORT_MODE_PULLUP      = 0x05
OCTOLINER_PORT_MODE_PULLDOWN    = 0x06
OCTOLINER_PORT_MODE_OUTPUT      = 0x07
OCTOLINER_DIGITAL_READ          = 0x08
OCTOLINER_DIGITAL_WRITE_HIGH    = 0x09
OCTOLINER_DIGITAL_WRITE_LOW     = 0x0A
OCTOLINER_ANALOG_WRITE          = 0x0B
OCTOLINER_ANALOG_READ           = 0x0C
OCTOLINER_PWM_FREQ              = 0x0D
OCTOLINER_ADC_SPEED             = 0x0E
OCTOLINER_PIN_INDEX_REV         = [4, 5, 6, 8, 7, 3, 2, 1]
OCTOLINER_PIN_INDEX             = [1, 2, 3, 7, 8, 6, 5, 4]

def getPiI2CBusNumber():
    """
    Returns the I2C bus number (/dev/i2c-#) for the Raspberry Pi being used.

    Courtesy quick2wire-python-api
    https://github.com/quick2wire/quick2wire-python-api
    """
    try:
        with open('/proc/cpuinfo','r') as f:
            for line in f:
                if line.startswith('Revision'):
                    return 1
    except:
        return 0

class оctoliner(object):
    """Troyka OCTOLINER"""

    def __init__(self, оctoliner_address=OCTOLINER_DEFAULT_I2C_ADDRESS):

        # Setup I2C interface for accelerometer and magnetometer.
        wp.wiringPiSetup()
        self._i2c = wp.I2C()
        self._io = self._i2c.setupInterface('/dev/i2c-' + str(getPiI2CBusNumber()), оctoliner_address)
#        self._оctoliner.write_byte(self._addr, OCTOLINER_RESET)

    def reverse_uint16(self, data):
        result = ((data & 0xff) << 8) | ((data>>8) & 0xff)
        return result

    def digitalReadPort(self):
        return self.reverse_uint16(self._i2c.readReg16(self._io, OCTOLINER_DIGITAL_READ))

    def digitalRead(self,  pin=range(8), Revers=False):
        if Revers: PIN_INDEX = OCTOLINER_PIN_INDEX_REV
        else: PIN_INDEX = OCTOLINER_PIN_INDEX
        a=[]
        portValue=self.digitalReadPort()
        for i in pin:
            mask = 0x0001 << PIN_INDEX[i]
            result = 0
            if portValue & mask:
                result = 1
            a.append(result)
        return a

    def analogRead16(self, pin):
        self._i2c.writeReg16(self._io, OCTOLINER_ANALOG_READ, pin)
        return self.reverse_uint16(self._i2c.readReg16(self._io, OCTOLINER_ANALOG_READ))

    def analogRead(self, pin=range(8), Revers=False):
        if Revers: PIN_INDEX = OCTOLINER_PIN_INDEX_REV
        else: PIN_INDEX = OCTOLINER_PIN_INDEX
        a=[]
        for i in pin:
            a.append(self.analogRead16(PIN_INDEX[i])/4095.0)
        return a

    def changeAddr(self, newAddr):
        self._i2c.writeReg16(self._io, OCTOLINER_CHANGE_I2C_ADDR, newAddr)

    def saveAddr(self):
        self._i2c.write(self._io, OCTOLINER_SAVE_I2C_ADDR)

    def reset(self):
        self._i2c.write(self._io, OCTOLINER_RESET)

    def setSensitivity(self, value=200, hard=True):
        pin=0
        value=int(value)
        if hard:
            if value in range(6): value = 200+value*11
            elif value<200: value = 200
            elif value>255:  value = 255
        else:
            if value<0: value = 0
            elif value>255:  value = 255
        data = (pin & 0xff)|((value & 0xff)<<8)
        self._i2c.writeReg16(self._io, OCTOLINER_ANALOG_WRITE, data)

    def setBrightness(self, value=True):
        pin=9
        sendData = self.reverse_uint16(0x0001<<pin)
        if value:
            self._i2c.writeReg16(self._io, OCTOLINER_DIGITAL_WRITE_HIGH, sendData)
        else:
            self._i2c.writeReg16(self._io, OCTOLINER_DIGITAL_WRITE_LOW, sendData)

