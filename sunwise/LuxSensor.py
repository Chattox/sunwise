import smbus2

class LuxSensor():
    """
    Tiny class for handling getting data from the DFRobot Gravity I2C ambient
    light sensor since there isn't a python library
    """
    def __init__(self):
        self.__port = 1
        self.__address = 0x23
        self.__register = 0x10
        self.__size = 2
        self.__bus = smbus2.SMBus(self.__port)

    def get_lux(self):
        """
        Read data from sensor and return as lux value

        Returns:
            float: light value as lux
        """

        # Read 2 bytes from the register
        buf = self.__bus.read_i2c_block_data(self.__address, self.__register, self.__size)

        if buf:
            # Combine the 2 bytes into a single 16-bit value
            data = (buf[0] << 8) | buf[1]

            lux = data / 1.2

            return lux
