from datetime import datetime, timezone

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

        now = datetime.now(timezone.utc)
        nowstr = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_entry = "{0} {1:<10} {2}".format(nowstr, "[" + level + "]:", text)

        print(log_entry)

        with open(self.__logfile, "a") as logfile:
            logfile.write(log_entry + "\n")

