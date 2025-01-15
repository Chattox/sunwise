import smbus2
import bme280

class Sensors():
    """
    Handles config and reading of attached sensors
    """
    def __init__(self):
        self.port = 1
        self.address = 0x77
        self.bus = smbus2.SMBus(self.port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    def get_bme280(self):
        """
        Get temperature, pressure, and humidity readings from the BME280

        Returns:
            dict: Temperature, humidity, and pressure readings rounded
            to 2 decimal places
        """
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        print(data.temperature)
        readings_dict = {
            "temperature": round(data.temperature, 2),
            "humidity": round(data.humidity, 2),
            "pressure": round(data.pressure, 2)
        }
        return readings_dict