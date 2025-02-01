from os import makedirs, path, listdir, remove
from json import dump, load
from datetime import datetime, timezone, timedelta
from time import sleep
from requests import post
from Sunwise.Logger import Logger
from Sunwise.Sensors import Sensors
from utils.datetime_string import datetime_string
from config import NICKNAME, READINGS_INCREMENT, UPLOAD_FREQUENCY, UPLOAD_DESTINATION, TIME_FORMAT, WIND_INTERVAL

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
                last_time_dt = datetime.strptime(last_time_str, TIME_FORMAT).replace(tzinfo=timezone.utc)
                self.last_reading_time = last_time_dt
        else:
            # If no last reading time file, set last_reading_time to force time trigger
            self.last_reading_time = self.last_reading_time - timedelta(minutes=READINGS_INCREMENT + 1)
        self.next_reading_time = self.last_reading_time
        self.next_wind_time = self.last_reading_time

    def take_readings(self):
        """
        Get data from all sensors and cache to readings file for later upload
        """
        self.logger.log("info", f"Last reading time: {self.last_reading_time.strftime(TIME_FORMAT)}")
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

    def upload_readings(self):
        """
        Upload cached readings to HTTP endpoint
        """
        upload_dir = listdir("uploads")
        upload_dir.sort()

        self.logger.log("info", f"Uploading {len(upload_dir)} readings...")
        self.logger.log("info", f"Destination: {UPLOAD_DESTINATION}")

        for reading_file in upload_dir:
                with open(f"uploads/{reading_file}", "r") as upload_file:
                    try:
                        res = post(UPLOAD_DESTINATION, json=(load(upload_file)))

                        if res.status_code in [200, 201, 202]:
                            remove(upload_file.name)
                            self.logger.log("info", f"- Uploaded {upload_file.name}")
                        else:
                            self.logger.log("error", f"- Upload of {upload_file.name} failed. Status: {res.status_code}, reason: {res.reason}")
                    except Exception as x:
                        self.logger.log("exception", f"An exception occurred when uploading: {x}")
                
    def check_triggers(self):
        """
        Check triggers which would be cause for taking readings such as time
        (and eventually rain sensor)
        """
        now = datetime.now(timezone.utc)
        trigger_time = self.next_reading_time.replace(second=0)
        
        if now >= self.next_wind_time:
            self.sensors.record_wind_speed()
            self.next_wind_time = now + timedelta(seconds=WIND_INTERVAL)

        if now >= trigger_time:
            self.logger.log("info", "Sleep interrupted. Reason for waking: Time trigger")
            self.take_readings()

            # Upload readings if there are enough cached to do so
            num_cached_readings = len(listdir("uploads"))
            self.logger.log("info", f"Cached readings: {num_cached_readings}. Upload every {UPLOAD_FREQUENCY} readings")
            if num_cached_readings >= UPLOAD_FREQUENCY:
                self.logger.log("info", f"Number of cached readings above specified upload frequency")
                self.upload_readings()

            # Calculate next time to take readings, then return to watch_weather loop
            minutes_to_next_reading = (READINGS_INCREMENT - (now.minute % READINGS_INCREMENT)) % READINGS_INCREMENT
            # If already on a readings interval increment, move to the next
            if minutes_to_next_reading == 0:
                minutes_to_next_reading = 15
            next_trigger_time = now + timedelta(minutes=minutes_to_next_reading)
            next_trigger_time.replace(second=0, microsecond=0)
            self.logger.log("info", f"Setting next reading time for {next_trigger_time.strftime(TIME_FORMAT)}")
            self.next_reading_time = next_trigger_time
            self.logger.log("info", "Returning to sleep...")

    def watch_weather(self):
        """
        Main loop of check triggers, act on them, sleep, repeat
        """
        self.logger.log("info", "Starting up...")
        self.logger.log("info", "- Setting up rain sensor")
        self.sensors.setup_rain_sensor()
        self.logger.log("info", "- Setting up anemometer")
        self.sensors.setup_anemometer()
        self.logger.log("info", "Startup complete, watching the weather...")

        while True:
            self.check_triggers()
            sleep(0.001)
            
