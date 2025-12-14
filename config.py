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
log = logging.getLogger()

BOLD = "\x1b[1m"
RESET = "\x1b[0m"

