import logging
from enum import StrEnum, auto

import colorlog
from colorlog import ColoredFormatter


class LogColor(StrEnum):
    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"
    BLUE = "\x1b[0;34m"
    RED = "\x1b[0;31m"
    MAGENTA = "\x1b[0;35m"
    GREEN = "\x1b[0;32m"
    YELLOW = "\x1b[0;33m"
    BLACK = "\x1b[0;30m"


class LogLevel(StrEnum):
    ERROR = "error"
    NOTE = "note"
    STUDENT = "student"
    SUCCESS = "success"
    WARNING = "warning"
    UNKNOWN = auto()

class Logger:
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname) %(message)s",
        datefmt=None,
        reset=True,
        log_colors= {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "purple"
        }
    )
    colorlog.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    def announce(self, message: str, level: StrEnum, pre_newline=False) -> None:
        color = ""

        match level.lower():
            case LogLevel.ERROR:
                color = LogColor.RED
            case LogLevel.NOTE | "info":
                color = LogColor.BLUE
            case LogLevel.STUDENT:
                color = LogColor.MAGENTA
            case LogLevel.SUCCESS:
                color = LogColor.GREEN
            case LogLevel.UNKNOWN | _:
                color = LogColor.BLACK

        if pre_newline:
            print(f"\n{color}{level}: {LogColor.RESET}{message}")
        else:
            print(f"{color}{level}: {LogColor.RESET}{message}")

    def note(self, leading: str, message: str, pre_newline=False):
        if pre_newline:
            print(f"\n{LogColor.BLACK}{leading}: {LogColor.RESET}{message}")
        else:
            print(f"{LogColor.BLACK}{leading}: {LogColor.RESET}{message}")

