import smbus2
import bme280

class Sensors():
    """
    Handles config and reading of attached sensors

    Args:
        logger (Logger): Logger instance
    """
    def __init__(self, logger):
        self.__logger = logger
        self.__port = 1
        self.__address = 0x77
        self.__bus = smbus2.SMBus(self.__port)
        self.__calibration_params = bme280.load_calibration_params(self.__bus, self.__address)

    def __get_bme280(self):
        """
        Get temperature, pressure, and humidity readings from the BME280

        Returns:
            dict: Temperature, humidity, and pressure readings rounded
            to 2 decimal places
        """
        data = bme280.sample(self.__bus, self.__address, self.__calibration_params)
        readings_dict = {
            "temperature": data.temperature,
            "humidity": data.humidity,
            "pressure": data.pressure
        }
        return readings_dict
    
    def get_readings(self):
        """
        Take readings from all sensors and return a dict containing them

        Returns:
            dict: sensor readings
        """
        self.__logger.log("info", "Taking new readings...")

        bme280_readings = self.__get_bme280()
        readings_dict = {
                "temperature": round(bme280_readings["temperature"], 2),
                "humidity": round(bme280_readings["humidity"], 2),
                "pressure": round(bme280_readings["pressure"], 2),
                "luminance": 0,
                "wind_speed": 0,
                "rain": 0,
                "rain_per_second": 0,
                "wind_direction": 0
        }

        return readings_dict
