from os import makedirs
from json import dump
from datetime import datetime
from Sunwise.Logger import Logger
from Sunwise.Sensors import Sensors
from utils.datetime_string import datetime_string

class Sunwise():
    """
    Handles overall functionality of the Sunwise weather station
    """

    def __init__(self):
        self.logger = Logger()
        self.sensors = Sensors(self.logger)

    def take_readings(self):
        """
        Get data from all sensors and cache to readings file for later upload
        """
        now = datetime_string()

        with open("last_reading_time.txt", "w") as timefile:
            timefile.write(now)

        readings = self.sensors.get_readings()
        cache_payload = {
            "nickname": "sunwise",
            "timestamp": now,
            "readings": readings
        }
        uploads_filename = f"uploads/{datetime_string(filename=True)}.json"

        makedirs("uploads", exist_ok=True)

        self.logger.log("info", "Caching readings for later upload")
        with open(uploads_filename, "w") as upload_file:
            dump(cache_payload, upload_file, indent=4)