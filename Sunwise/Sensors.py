import smbus2
import bme280
import warnings
import math
import os
from gpiozero import PinFactoryFallback, Button
from utils.datetime_string import datetime_string
from config import RAIN_SENSOR_MM, WIND_RADIUS, WIND_INTERVAL, WIND_ADJUSTMENT



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
        self.__wind_speed_sensor = Button(5)
        self.__wind_count = 0

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

        with open("rain.txt", "a") as rainfile:
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
        if not os.path.isfile("rain.txt"):
            return 0

        rain_mm = 0

        with open("rain.txt", "r") as rainfile:
            rain_data = rainfile.readlines()
        
        for entry in rain_data:
            if entry:
                rain_mm += RAIN_SENSOR_MM

        os.remove("rain.txt")

        return rain_mm
    
    def __spin(self):
        """
        Record a single half rotation of the anemometer
        
        Note:
            It's a half rotation due to the anemometer generating two signals
            per whole rotation
        """
        self.__wind_count += 1

    def setup_anemometer(self):
        """
        Sets up the listener for the anemometer
        """
        self.__wind_speed_sensor.when_activated = self.__spin
        self.__logger.log("info", "- Anemometer sensor setup complete")

    def record_wind_speed(self):
        """
        Calculates wind speed from wind_count and WIND_INTERVAL and
        stores to file
        """
        circumference_cm = (2 * math.pi) * WIND_RADIUS
        rotations = self.__wind_count / 2.0

        # Distance travelled by an anemometer cup in cm
        dist_cm = circumference_cm * rotations

        # Wind speed, convert to m/s and adjust for anemometer factor
        speed = ((dist_cm / WIND_INTERVAL) / 100) * WIND_ADJUSTMENT

        # Save to file
        with open("wind.txt", "a") as windfile:
            windfile.write(str(speed) + "\n")

        self.__wind_count = 0
        
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
