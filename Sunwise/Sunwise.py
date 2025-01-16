from os import makedirs, path
from json import dump
from datetime import datetime, timezone, timedelta
from time import sleep
from Sunwise.Logger import Logger
from Sunwise.Sensors import Sensors
from utils.datetime_string import datetime_string
from config import NICKNAME, READINGS_INTERVAL

class Sunwise():
    """
    Handles overall functionality of the Sunwise weather station
    """

    def __init__(self):
        self.logger = Logger()
        self.sensors = Sensors(self.logger)
        self.last_reading_time = datetime.now(timezone.utc)
        if path.isfile("last_reading_time.txt"):
            with open("last_reading_time.txt", "r") as timefile:
                last_time_str = timefile.readline()
                last_time_dt = datetime.strptime(last_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                self.last_reading_time = last_time_dt
        self.reading_interval = timedelta(minutes=READINGS_INTERVAL)
        self.next_reading_time = self.last_reading_time + self.reading_interval

    def take_readings(self):
        """
        Get data from all sensors and cache to readings file for later upload
        """
        self.logger.log("info", f"Last reading time: {self.last_reading_time}")
        now_str = datetime_string()
        now_dt = datetime.now(timezone.utc)

        with open("last_reading_time.txt", "w") as timefile:
            timefile.write(now_str)
            self.last_reading_time = now_dt

        readings = self.sensors.get_readings()
        cache_payload = {
            "nickname": NICKNAME,
            "timestamp": now_str,
            "readings": readings
        }
        uploads_filename = f"uploads/{datetime_string(filename=True)}.json"

        makedirs("uploads", exist_ok=True)

        self.logger.log("info", "Caching readings for later upload")
        with open(uploads_filename, "w") as upload_file:
            dump(cache_payload, upload_file, indent=4)

    def check_triggers(self):
        """
        Check triggers which would be cause for taking readings such as time
        (and eventually rain sensor)
        """
        now = datetime.now(timezone.utc)
        trigger_time = self.next_reading_time.replace(second=0)
        
        if now >= trigger_time:
            self.take_readings()
            next_trigger_time = self.last_reading_time + self.reading_interval
            next_trigger_time = next_trigger_time.replace(second=0)
            self.logger.log("info", f"Setting next reading time for {next_trigger_time}")
            self.next_reading_time = next_trigger_time

    def main_loop(self):
        """
        Main loop of check triggers, act on them, sleep, repeat
        """
        self.logger.log("info", "Starting main loop")

        while True:
            self.check_triggers()
            sleep(0.001)
            
