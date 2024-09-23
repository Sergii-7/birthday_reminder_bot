from datetime import datetime
import pytz


def correct_time(timezone_: str = 'Europe/Kyiv') -> datetime:
    """ Back time now 'Europe/Kyiv': object=datetime """
    return datetime.now(tz=pytz.timezone(timezone_)).replace(tzinfo=None)