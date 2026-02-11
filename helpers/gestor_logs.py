import logging
import sys


class Logger(logging.Logger):
    """
    Logger class.

    Parameters
    ----------
    name : str, optional
        Logger name, default is "pvcontrol".
    level : int, optional
        Logging level, default is logging.INFO.

    Notes
    -----
    If the logger has no handlers, it will add a StreamHandler
    and a Formatter to display the log messages in the format
    "%(asctime)s %(levelname)s [%(processName)s] %(name)s: %(message)s".
    The propagate flag is set to False so that the log messages are
    not propagated to the root logger.
    """
    
    # def __init__(self, name="pvcontrol", level=logging.INFO):
    #     super().__init__(name, level)

    #     if not self.handlers:
    #         handler = logging.StreamHandler(sys.stdout)
    #         formatter = logging.Formatter(
    #             "%(asctime)s %(levelname)s [%(processName)s] %(name)s: %(message)s"
    #         )
    #         handler.setFormatter(formatter)
    #         self.addHandler(handler)
    #         self.propagate = False

    # def info(self, msg, end="\n"):
    #     print(msg, end=end)

    # def debug(self, msg, end="\n"):
    #     print(msg, end=end)

    # def error(self, msg, end="\n"):
    #     print(msg, end=end)

    # def always(self, msg, end="\n"):
    #     print(msg, end=end)

    # def is_debug(self):
    #     return self._log.level <= logging.DEBUG
    
    # def is_info(self):
    #     return self._log.level <= logging.INFO

    def __init__(self, *, level=logging.INFO, name=None):
        """
        Simple per-script logger.

        Args:
            level: logging level (logging.DEBUG, logging.INFO, etc.)
            name: optional string name for the logger
        """
        self._log = logging.getLogger(name or str(id(self)))
        self._log.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._log.handlers.clear()
        self._log.addHandler(handler)

    def info(self, msg, end="\n"):
        if self._log.isEnabledFor(logging.INFO):
            print(msg, end=end)

    def debug(self, msg, end="\n"):
        if self._log.isEnabledFor(logging.DEBUG):
            print(msg, end=end)

    def error(self, msg, end="\n"):
        print(msg, end=end)

    def always(self, msg, end="\n"):
        print(msg, end=end)

    # helpers
    def is_debug(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def is_info(self):
        return self._log.isEnabledFor(logging.INFO)