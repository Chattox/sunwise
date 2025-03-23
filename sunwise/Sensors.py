import smbus2
import bme280
import warnings
import math
import os
import statistics
from gpiozero import PinFactoryFallback, Button, MCP3008
from sunwise.LuxSensor import LuxSensor
from utils import datetime_string
from config import RAIN_SENSOR_MM, WIND_RADIUS, WIND_INTERVAL, WIND_ADJUSTMENT, WIND_DIR_VOLTS

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
        self.__bme280_address = 0x77
        self.__lux_sensor = LuxSensor()
        self.__bus = smbus2.SMBus(self.__port)
        self.__calibration_params = bme280.load_calibration_params(self.__bus, self.__bme280_address)
        self.__rain_sensor = Button(6)
        self.__wind_speed_sensor = Button(5)
        self.__wind_count = 0
        self.__wind_direction_sensor = MCP3008(channel=0)
        self.__wind_dir_data = []

    def __get_bme280(self):
        """
        Get temperature, pressure, and humidity readings from the BME280

        Returns:
            dict: Temperature, humidity, and pressure readings rounded
            to 2 decimal places
        """
        data = bme280.sample(self.__bus, self.__bme280_address, self.__calibration_params)
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
        Record a single half rotation of the anemometer as well as wind direction
        
        Note:
            It's a half rotation due to the anemometer generating two signals
            per whole rotation
        """
        self.__wind_count += 1
        self.__record_wind_direction()

    def setup_anemometer(self):
        """
        Sets up the listener for the anemometer
        """
        self.__wind_speed_sensor.when_activated = self.__spin
        self.__logger.log("info", "- Anemometer sensor setup complete")

    def record_wind_data(self):
        """
        Calculates wind speed from wind_count and WIND_INTERVAL and
        average wind direction and stores to file
        """
        circumference_cm = (2 * math.pi) * WIND_RADIUS
        rotations = self.__wind_count / 2.0

        # Distance travelled by an anemometer cup in cm
        dist_cm = circumference_cm * rotations

        # Wind speed, convert to m/s and adjust for anemometer factor
        speed = ((dist_cm / WIND_INTERVAL) / 100) * WIND_ADJUSTMENT

        # Finally get average wind direction
        average_wind_dir = 0.0
        if len(self.__wind_dir_data) > 0:
            average_wind_dir = self.__get_average_wind_dir()
        elif os.path.isfile("wind_dir.txt"):
            # If there's not been any wind, duplicate the most recent dir since
            # the vane won't have moved
            with open("wind_dir.txt", "r") as read_dirfile:
                last_dir = read_dirfile.readlines()[-1].rstrip()
        # If there's no wind or previous dir, just leave it as 0.0. Should probably
        # look into always storing most recent dir for this

        # Save to file
        with open("wind_speed.txt", "a") as speedfile:
            speedfile.write(str(speed) + "\n")
        
        with open("wind_dir.txt", "a") as dirfile:
            dirfile.write(str(average_wind_dir) + "\n")

        self.__wind_count = 0
        self.__wind_dir_data = []

    def __get_average_wind_dir(self, data=[]):
        """
        Get average wind direction from list of readings. Maths shamelessly stolen from
        the internet because I'm a dev, not a shape wizard

        Returns:
            int: angle of average wind direction
        """
        if len(data) == 0:
            data = self.__wind_dir_data

        sin_sum = 0.0
        cos_sum = 0.0

        for angle in data:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        f_len = float(len(data))
        s = sin_sum / f_len
        c = cos_sum / f_len
        if s == 0.0 or c == 0.0:
            self.__logger.log("debug", f"f_len: {f_len}, sin_sum: {sin_sum}, cos_sum: {cos_sum}\ns: {s}, c: {c}")
            # dump wind dir data to file for debugging
            with open(f"debug_wind_dir-{datetime_string(filename=True)}.txt", "a") as debugfile:
                debugfile.write([str(i)+"\n" for i in data])
        arc = math.degrees(math.atan(s / c))
        average = 0.0

        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average

    def __record_wind_direction(self):
        """
        Record current wind direction based on voltage reading from vane to memory
        """
        wind_dir = round(self.__wind_direction_sensor.value*3.3,1)
        # TODO: On bad readings, find closest angle and save that instead
        if wind_dir in WIND_DIR_VOLTS:
            self.__wind_dir_data.append(WIND_DIR_VOLTS[wind_dir])

    def __get_wind_speed_data(self):
        """
        Calculate average wind speed and gust speed from currently saved readings 

        Returns:
            float: average wind speed in m/s
            float: gust speed in m/s
        """
        wind_speeds = []
        with open("wind_speed.txt", "r") as speedfile:
            speeds = speedfile.readlines()
            for speed in speeds:
                f_speed = float(speed.rstrip())
                wind_speeds.append(f_speed)

        gust = max(wind_speeds)
        avg_speed = statistics.mean(wind_speeds)

        os.remove("wind_speed.txt")

        return gust, avg_speed

    def __get_wind_dir_data(self):
        """
        Calculate average wind direction from currently saved readings

        Returns:
            float: average angle of wind direction
        """
        wind_dirs = []
        with open("wind_dir.txt", "r") as dirfile:
            dirs = dirfile.readlines()
            for dir in dirs:
                f_dir = float(dir.rstrip())
                wind_dirs.append(f_dir)
        
        average_dir = self.__get_average_wind_dir(wind_dirs)
        
        # Return closest cardinal/ordinal angle
        compass_angles = [0, 45, 90, 135, 180, 225, 270, 315, 360]
        closest_angle = min(compass_angles, key=lambda x: abs(x - average_dir))

        os.remove("wind_dir.txt")

        return 0 if closest_angle == 360 else closest_angle
    
    def get_readings(self):
        """
        Take readings from all sensors and return a dict containing them

        Returns:
            dict: sensor readings
        """
        self.__logger.log("info", "Taking new readings...")

        bme280_readings = self.__get_bme280()
        rainfall = self.__get_rainfall()
        gust, avg_speed = self.__get_wind_speed_data()
        wind_dir = self.__get_wind_dir_data()
        lux = self.__lux_sensor.get_lux()
        readings_dict = {
                "temperature": bme280_readings["temperature"],
                "humidity": bme280_readings["humidity"],
                "pressure": bme280_readings["pressure"],
                "luminance": lux,
                "wind_speed": avg_speed,
                "gust_speed": gust,
                "wind_direction": wind_dir,
                "rain": rainfall,
                "rain_per_second": 0,
        }

        return readings_dict
