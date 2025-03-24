# Software constants
# Name of the station to identify it in the readings database
STATION_NAME = ""
# Increment on the hour to take readings. e.g. 15 means readings at 0, 15, 30, and 45, minutes
# past the hour
READINGS_INCREMENT = 15
# How many reading files to store before uploading them
UPLOAD_FREQUENCY = 4
# HTTP endpoint to upload readings to
UPLOAD_DESTINATION = ""
# Format for string representations of timestamps
TIME_FORMAT = ""
# How often to calculate and record wind speed in seconds
WIND_INTERVAL = 5
# Adjustment for anemometer factor
WIND_ADJUSTMENT = 1.1789
# Dict for looking up wind direction angle based on wind vane voltage
WIND_DIR_VOLTS = {0.4: 0.0,
                  1.4: 22.5,
                  1.2: 45.0,
                  2.8: 67.5,
                  2.7: 90.0,
                  2.9: 112.5,
                  2.2: 135.0,
                  2.5: 157.5,
                  1.8: 180.0,
                  2.0: 202.5,
                  0.7: 225.0,
                  0.8: 247.5,
                  0.1: 270.0,
                  0.3: 292.5,
                  0.2: 315.0,
                  0.6: 337.5}

# Hardware constants
# Amount of rain required for the rain sensor to trip in mm
RAIN_SENSOR_MM = 0.2794
# Radius of anemometer in cm
WIND_RADIUS = 9.0
