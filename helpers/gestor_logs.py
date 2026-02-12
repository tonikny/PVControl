import logging
import os

class Logger:
    """
    Logger class.

    Parameters:
    
    level : int, optional
        Logging level, default is logging.ERROR or environment variable LOGLEVEL
    name : str, optional
        Logger name, default is "pvcontrol".
    """

    def __init__(self, name="pvcontrol", level=logging.ERROR):
        """
        Simple per-script logger.

        Args:
            level: logging level
            name: optional string name for the logger
        """
        self._log = logging.getLogger(name)
        self._log.setLevel(level=os.getenv('LOGLEVEL', str(level)).upper())
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] [%(processName)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        self._log.handlers.clear()
        self._log.addHandler(handler)
        # self._log.propagate = False

    def debug(self, *msg):
        self._log.debug(" ".join(msg))

    def info(self, *msg):
        self._log.info(" ".join(msg))

    def warning(self, *msg):
        self._log.warning(" ".join(msg))

    def error(self, *msg):
        self._log.error(" ".join(msg))

    def manual(self, *msg):
        formatter = self._log.handlers[0].formatter
        assert isinstance(formatter, logging.Formatter)
        orig = formatter._style._fmt
        formatter._style._fmt = "[MANUAL] [%(processName)s] %(name)s: %(message)s"
        self._log.critical(" ".join(msg))
        formatter._style._fmt = orig

    # helpers
    def is_debug(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def is_info(self):
        return self._log.isEnabledFor(logging.INFO)