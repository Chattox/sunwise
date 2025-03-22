from utils import datetime_string

class Logger():
    """
    Handles logging info, errors, etc to file
    """
    def __init__(self):
        self.__logfile = "log.txt"

    def log(self, level, text):
        """
        Log info to file

        Args:
            level (str): logging level such as debug, error, etc
            text (Str): info to log
        """

        now = datetime_string()

        log_entry = "{0} {1:<10} {2}".format(now, "[" + level + "]:", text)

        print(log_entry)

        with open(self.__logfile, "a") as logfile:
            logfile.write(log_entry + "\n")

