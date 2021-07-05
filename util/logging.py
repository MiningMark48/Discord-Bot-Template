import logging


class Colors:
    """
    Colors used for logging.
    """

    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strike_through = '\033[09m'
    invisible = '\033[08m'

    class FG:
        """
        Foreground colors
        """

        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        light_grey = '\033[37m'
        dark_grey = '\033[90m'
        light_red = '\033[91m'
        light_green = '\033[92m'
        yellow = '\033[93m'
        light_blue = '\033[94m'
        pink = '\033[95m'
        light_cyan = '\033[96m'

    class BG:
        """
        Background colors
        """

        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        light_grey = '\033[47m'


class ConsoleColorFormatter(logging.Formatter):
    """Logging formatter to add colors"""

    def __init__(self, format: str, date_format: str, style: str, colored=True):

        self.fmt = format
        self.date_format = date_format
        self.style = style
        self.colored = colored
        
        f = lambda c: c + format + Colors.reset

        self.formats = {
            logging.DEBUG: f(Colors.FG.purple),
            logging.INFO: f(Colors.FG.light_grey),
            logging.WARNING: f(Colors.FG.orange),
            logging.ERROR: f(Colors.FG.red),
            logging.CRITICAL: f(Colors.FG.pink)
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno) if self.colored else self.fmt
        formatter = logging.Formatter(log_fmt, self.date_format, self.style)
        return formatter.format(record)