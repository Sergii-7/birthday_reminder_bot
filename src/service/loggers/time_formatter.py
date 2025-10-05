from datetime import datetime
from logging import Formatter

import pytz


class KyivTimeFormatter(Formatter):
    """Setting Kyiv time."""

    timezone_: str = "Europe/Kyiv"

    def formatTime(self, record, datefmt=None) -> str:
        kyiv_time = datetime.now(tz=pytz.timezone(self.timezone_)).replace(tzinfo=None)
        return kyiv_time.strftime("%Y-%m-%d %H:%M:%S")
