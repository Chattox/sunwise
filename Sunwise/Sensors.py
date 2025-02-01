import smbus2
import bme280
import warnings
from os import remove, path
from gpiozero import PinFactoryFallback
from gpiozero import Button
from utils.datetime_string import datetime_string
from config import RAIN_SENSOR_MM



class Sensors():
    """
    Handles config and reading of attached sensors

    Args:
        logger (Logger): Logger instance
    """
    def __init__(self, logger):
        warnings.simplefilter("ignore", PinFactoryFallback)
        self.__logger = logger
        self.__port = 1
        self.__address = 0x77
        self.__bus = smbus2.SMBus(self.__port)
        self.__calibration_params = bme280.load_calibration_params(self.__bus, self.__address)
        self.__rain_sensor = Button(6)

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

    def __record_rainfall(self):
        """
        Records rainfall when rain sensor is tripped and saves to file
        """
        self.__logger.log("info", "Recording detected rainfall")
        now_str = datetime_string()

        with open("rainfall.txt", "a") as rainfile:
            rainfile.write(now_str + "\n")

    def setup_rain_sensor(self):
        """
        Sets up the listener for the rain sensor
        """
        self.__rain_sensor.when_activated = self.__record_rainfall
        self.__logger.log("info", "- Rainfall sensor setup complete")

    def __get_rainfall(self):
        """
        Multiplies the number of rain sensor readings in rain.txt by RAIN_SENSOR_MM
        to get total rainfall in mm

        Returns:
            int: amount of rainfall in mm
        """
        if not path.isfile("rain.txt"):
            return 0

        rain_mm = 0

        with open("rain.txt", "r") as rainfile:
            rain_data = rainfile.readlines()
        
        for entry in rain_data:
            if entry:
                rain_mm += RAIN_SENSOR_MM

        remove("rain.txt")

        return rain_mm
    
    def get_readings(self):
        """
        Take readings from all sensors and return a dict containing them

        Returns:
            dict: sensor readings
        """
        self.__logger.log("info", "Taking new readings...")

        bme280_readings = self.__get_bme280()
        rainfall = self.__get_rainfall()
        readings_dict = {
                "temperature": round(bme280_readings["temperature"], 2),
                "humidity": round(bme280_readings["humidity"], 2),
                "pressure": round(bme280_readings["pressure"], 2),
                "luminance": 0,
                "wind_speed": 0,
                "rain": rainfall,
                "rain_per_second": 0,
                "wind_direction": 0
        }

        return readings_dict
