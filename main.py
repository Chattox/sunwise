from traceback import format_exc
from sunwise.Sunwise import Sunwise
from utils import datetime_string

try:
    sunwise = Sunwise()
    sunwise.watch_weather()
except Exception as e:
    now = datetime_string()

    log_entry = "{0} {1:<10} {2}".format(now, "[exception]: ", format_exc())

    print(log_entry)

    with open("log.txt", "a") as logfile:
        logfile.write(log_entry + "\n")
