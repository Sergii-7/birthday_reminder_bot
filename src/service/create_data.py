from typing import Optional

from src.service.loggers.py_logger_tel_bot import get_logger
from src.sql.models import User

logger = get_logger(__name__)


def user_data(user: User, is_birthday: bool = True) -> Optional[str]:
    """Create text data about User by Data from Telegram."""
    try:
        last_name = f"\n{user.last_name}" if user.last_name else ""
        username = f"\n@{user.username}" if user.username else ""
        phone_number = f"\n{user.phone_number}" if user.phone_number else ""
        if is_birthday:
            birthday = f"\nдата народження (місяць-день): {str(user.birthday)[5:]}" if user.birthday else ""
            data_text = f"<u>іменинник(іменинниця)</u>:\n{user.first_name}{last_name}{username}{phone_number}{birthday}"
        else:
            data_text = f"{user.first_name}{last_name}{username}{phone_number}"
        return data_text
    except Exception as e:
        logger.error(msg=str(e))
    return None
